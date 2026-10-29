import pytest
from fastapi.testclient import TestClient

from app import api
from cargar_csv import load_fixture


@pytest.fixture(autouse=True)
def fresh_orders():
    """Cada prueba parte de datos limpios (el repositorio es en memoria)."""
    api.orders.clear()
    api.orders.update(load_fixture())


client = TestClient(api.app)


def test_get_pedido():
    r = client.get("/orders/O001")
    assert r.status_code == 200
    assert r.json()["units"] == 4 and r.json()["total"] == "2100.00"


def test_404_pedido_inexistente():
    assert client.post("/orders/NOPE/confirm").status_code == 404
    assert client.get("/orders/NOPE").status_code == 404


def test_confirmar_ok():
    r = client.post("/orders/O013/confirm")
    assert r.status_code == 200
    assert r.json()["status"] == "CONFIRMED"
    assert r.json()["events"] == ["OrderConfirmed"]


def test_409_confirmar_dos_veces():
    client.post("/orders/O013/confirm")
    r = client.post("/orders/O013/confirm")
    assert r.status_code == 409
    assert client.get("/orders/O013").json()["events"] == ["OrderConfirmed"]


def test_422_confirmar_pedido_vacio():
    assert client.post("/orders/O007/confirm").status_code == 422


def test_422_cliente_inactivo():
    assert client.post("/orders/O003/confirm").status_code == 422


def test_envio_sin_guia_422():
    client.post("/orders/O012/confirm")
    r = client.post("/orders/O012/ship", json={"tracking_number": ""})
    assert r.status_code == 422
    assert client.get("/orders/O012").json()["status"] == "CONFIRMED"


def test_cancelar_desde_shipped_409():
    client.post("/orders/O014/confirm")
    assert client.post("/orders/O014/ship", json={"tracking_number": "G1"}).status_code == 200
    r = client.post("/orders/O014/cancel", json={"reason": "tarde"})
    assert r.status_code == 409
    assert client.get("/orders/O014").json()["status"] == "SHIPPED"


def test_flujo_entrega_y_devolucion():
    client.post("/orders/O016/confirm")
    client.post("/orders/O016/ship", json={"tracking_number": "G3"})
    assert client.post("/orders/O016/deliver").json()["status"] == "DELIVERED"
    client.post("/orders/O015/confirm")
    client.post("/orders/O015/ship", json={"tracking_number": "G2"})
    assert client.post("/orders/O015/return").json()["status"] == "RETURNED"


def test_descuento_endpoint():
    assert client.get("/orders/O001/discount").json()["rate"] == "0.10"
    assert client.get("/orders/O006/discount").json()["rate"] == "0.05"
