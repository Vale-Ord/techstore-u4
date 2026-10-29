from decimal import Decimal

import pytest

from app.domain import (
    Customer, InvalidOrderData, InvalidOrderTransition, Money, Order,
    OrderItem, OrderItemLimitExceeded, OrderStatus,
)
from cargar_csv import load_fixture


def item(qty=1, price="100.00", sku="SKU001"):
    return OrderItem(sku, qty, Money(Decimal(price)))


# ---------------------------------------------------------------- Money / VO
def test_money_negativo():
    with pytest.raises(InvalidOrderData):
        Money(Decimal("-1"))


def test_money_rechaza_float():
    with pytest.raises(InvalidOrderData):
        Money(600.0)


def test_money_add_y_monedas_distintas():
    assert Money(Decimal("100")).add(Money(Decimal("50"))).amount == Decimal("150")
    with pytest.raises(InvalidOrderData):
        Money(Decimal("1"), "MXN").add(Money(Decimal("1"), "USD"))


def test_money_inmutable():
    m = Money(Decimal("10"))
    with pytest.raises(Exception):
        m.amount = Decimal("20")


def test_orderitem_cantidad_invalida():
    with pytest.raises(InvalidOrderData):
        item(qty=0)
    with pytest.raises(InvalidOrderData):
        item(qty=-2)


# ------------------------------------------------------------------- carga
def test_pedido_o001_inicia_draft():
    orders = load_fixture()
    assert len(orders) == 16
    assert orders["O001"].status.value == "DRAFT"
    assert orders["O001"].units == 4
    assert orders["O001"].total.amount == Decimal("2100.00")


# ------------------------------------------------------------------- límite
def test_20_unidades_exactas_permitidas():
    assert load_fixture()["O008"].units == 20


def test_21_unidades_rechazadas_sin_modificar_pedido():
    o = load_fixture()["O009"]
    with pytest.raises(OrderItemLimitExceeded):
        o.add_item(item(qty=2, price="120.00", sku="SKU003"))
    assert o.units == 19 and len(o.items) == 1


def test_limite_cuenta_unidades_no_renglones():
    o = Order(Customer("C1"), "X")
    o.add_item(item(qty=10))
    o.add_item(item(qty=10, sku="SKU002"))  # 2 renglones, 20 unidades
    with pytest.raises(OrderItemLimitExceeded):
        o.add_item(item(qty=1, sku="SKU003"))


def test_no_se_agregan_items_fuera_de_draft():
    o = load_fixture()["O013"]
    o.confirm()
    with pytest.raises(InvalidOrderTransition):
        o.add_item(item())


# ----------------------------------------------------------- máquina de estados
def test_confirmar_pedido_vacio():
    o = load_fixture()["O007"]
    with pytest.raises(InvalidOrderData):
        o.confirm()
    assert o.status == OrderStatus.DRAFT and o.events == []


def test_confirmar_cliente_inactivo():
    o = load_fixture()["O003"]
    with pytest.raises(InvalidOrderData):
        o.confirm()
    assert o.status == OrderStatus.DRAFT and o.events == []


def test_confirmar_exito_registra_evento():
    o = load_fixture()["O013"]
    o.confirm()
    assert o.status == OrderStatus.CONFIRMED
    assert [e.name for e in o.events] == ["OrderConfirmed"]


def test_confirmacion_doble_no_duplica_evento():
    o = load_fixture()["O013"]
    o.confirm()
    with pytest.raises(InvalidOrderTransition):
        o.confirm()
    assert len(o.events) == 1


@pytest.mark.parametrize("guia", ["", "   ", None])
def test_envio_sin_guia(guia):
    o = load_fixture()["O012"]
    o.confirm()
    with pytest.raises(InvalidOrderData):
        o.ship(guia)
    assert o.status == OrderStatus.CONFIRMED
    assert [e.name for e in o.events] == ["OrderConfirmed"]


def test_cancelacion_desde_shipped_rechazada():
    o = load_fixture()["O014"]
    o.confirm()
    o.ship("GUIA-1")
    with pytest.raises(InvalidOrderTransition):
        o.cancel("ya no lo quiero")
    assert o.status == OrderStatus.SHIPPED
    assert [e.name for e in o.events] == ["OrderConfirmed", "OrderShipped"]


def test_cancelacion_requiere_motivo():
    o = load_fixture()["O013"]
    o.confirm()
    with pytest.raises(InvalidOrderData):
        o.cancel("  ")
    assert o.status == OrderStatus.CONFIRMED


def test_cancelacion_valida():
    o = load_fixture()["O013"]
    o.confirm()
    o.cancel("error en el pedido")
    assert o.status == OrderStatus.CANCELLED
    assert o.events[-1].name == "OrderCancelled"


def test_devolucion_y_entrega_validas():
    r = load_fixture()["O015"]
    r.confirm(); r.ship("G-2"); r.return_order()
    assert r.status == OrderStatus.RETURNED
    d = load_fixture()["O016"]
    d.confirm(); d.ship("G-3"); d.deliver()
    assert d.status == OrderStatus.DELIVERED
    assert [e.name for e in d.events] == ["OrderConfirmed", "OrderShipped", "OrderDelivered"]


def test_entregar_o_devolver_desde_draft_rechazado():
    o = load_fixture()["O013"]
    with pytest.raises(InvalidOrderTransition):
        o.deliver()
    with pytest.raises(InvalidOrderTransition):
        o.return_order()
    assert o.events == []
