from decimal import Decimal

import pytest

from app.specifications import (
    ActivePromotionSpec, MinimumAmountSpec, MinimumUnitsSpec, VIPCustomerSpec,
    discount_amount, discount_rate, total_with_discount,
)
from cargar_csv import load_fixture


@pytest.mark.parametrize("pid,esperado", [
    ("O001", "0.10"),   # E01 VIP, 2100, 4 u, sin promo
    ("O002", "0"),      # E02 no VIP
    ("O005", "0"),      # E04 promo activa
    ("O006", "0.05"),   # E05 total > 5000
    ("O010", "0"),      # E09 total == 500 (umbral estricto)
    ("O011", "0"),      # E10 solo 3 unidades
])
def test_tasa_de_descuento(pid, esperado):
    assert discount_rate(load_fixture()[pid]) == Decimal(esperado)


def test_montos_de_descuento():
    o = load_fixture()
    assert discount_amount(o["O001"]).amount == Decimal("210.000")
    assert total_with_discount(o["O001"]).amount == Decimal("1890.000")
    assert total_with_discount(o["O006"]).amount == Decimal("17100.00")


def test_umbral_500_es_estricto():
    o = load_fixture()["O010"]
    assert o.total.amount == Decimal("500.00")
    assert not MinimumAmountSpec(Decimal("500")).is_satisfied_by(o)


def test_minimo_4_unidades():
    o = load_fixture()["O011"]
    assert not MinimumUnitsSpec(4).is_satisfied_by(o)
    assert MinimumUnitsSpec(3).is_satisfied_by(o)


def test_specs_individuales_con_and_or_not():
    o = load_fixture()["O005"]  # VIP, 2100, 4 u, con promo
    assert VIPCustomerSpec().is_satisfied_by(o)
    assert ActivePromotionSpec().is_satisfied_by(o)
    assert not (~ActivePromotionSpec()).is_satisfied_by(o)
    assert (VIPCustomerSpec() | ActivePromotionSpec()).is_satisfied_by(o)
    assert not (VIPCustomerSpec() & ~ActivePromotionSpec()).is_satisfied_by(o)


def test_prioridad_10_sobre_5():
    # VIP, >5000, >=4 unidades, sin promo: cumple ambas reglas -> 10 %
    from app.domain import Customer, Money, Order, OrderItem
    o = Order(Customer("V", is_vip=True), "P")
    o.add_item(OrderItem("SKU008", 4, Money(Decimal("18000.00"))))
    assert discount_rate(o) == Decimal("0.10")


def test_evaluar_no_modifica_el_pedido():
    o = load_fixture()["O001"]
    discount_rate(o)
    assert o.status.value == "DRAFT" and o.events == [] and o.units == 4
