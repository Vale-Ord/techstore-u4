"""API REST: controladores delgados. Toda regla vive en app.domain."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.domain import (
    DomainException, InvalidOrderData, InvalidOrderTransition,
    Order, OrderItemLimitExceeded,
)
from app.specifications import discount_amount, discount_rate, total_with_discount
from cargar_csv import load_fixture

app = FastAPI(title="TechStore U4", description="Núcleo de negocio de pedidos")
orders: dict[str, Order] = load_fixture()


class ShipRequest(BaseModel):
    tracking_number: str


class CancelRequest(BaseModel):
    reason: str


# ----- Traducción excepción de dominio -> HTTP semántico
@app.exception_handler(InvalidOrderTransition)
async def _transition(_: Request, exc: InvalidOrderTransition):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(InvalidOrderData)
async def _invalid_data(_: Request, exc: InvalidOrderData):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(OrderItemLimitExceeded)
async def _limit(_: Request, exc: OrderItemLimitExceeded):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


def _get(order_id: str) -> Order:
    order = orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="No existe")
    return order


def _dto(order: Order) -> dict:
    return {
        "id": order.id,
        "customer_id": order.customer.id,
        "status": order.status.value,
        "units": order.units,
        "total": str(order.total.amount),
        "events": [e.name for e in order.events],
    }


@app.get("/orders/{order_id}")
def get_order(order_id: str):
    return _dto(_get(order_id))


@app.get("/orders/{order_id}/discount")
def get_discount(order_id: str):
    order = _get(order_id)
    return {
        "id": order.id,
        "rate": str(discount_rate(order)),
        "discount": str(discount_amount(order).amount),
        "total_with_discount": str(total_with_discount(order).amount),
    }


@app.post("/orders/{order_id}/confirm")
def confirm_order(order_id: str):
    order = _get(order_id)
    order.confirm()
    return _dto(order)


@app.post("/orders/{order_id}/ship")
def ship_order(order_id: str, body: ShipRequest):
    order = _get(order_id)
    order.ship(body.tracking_number)
    return _dto(order)


@app.post("/orders/{order_id}/cancel")
def cancel_order(order_id: str, body: CancelRequest):
    order = _get(order_id)
    order.cancel(body.reason)
    return _dto(order)


@app.post("/orders/{order_id}/deliver")
def deliver_order(order_id: str):
    order = _get(order_id)
    order.deliver()
    return _dto(order)


@app.post("/orders/{order_id}/return")
def return_order(order_id: str):
    order = _get(order_id)
    order.return_order()
    return _dto(order)
