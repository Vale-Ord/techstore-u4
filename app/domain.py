"""Núcleo de dominio TechStore (Actividad 4).

No depende de FastAPI ni de ninguna infraestructura: se puede ejecutar
y probar completamente en memoria.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

MAX_UNITS = 20


# ---------------------------------------------------------------- Excepciones
class DomainException(Exception):
    """Violación de una regla de negocio (no una falla técnica)."""


class OrderException(DomainException):
    pass


class InvalidOrderData(OrderException):
    """Datos que violan una invariante (monto negativo, pedido vacío, etc.)."""


class InvalidOrderTransition(OrderException):
    """La operación no es válida desde el estado actual."""


class OrderItemLimitExceeded(OrderException):
    """Se excede el máximo de 20 unidades por pedido."""


# --------------------------------------------------------------- Value Objects
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "MXN"

    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            # Rechaza float/int para evitar errores de redondeo binario.
            raise InvalidOrderData("El monto debe ser Decimal")
        if not self.amount.is_finite() or self.amount < 0:
            raise InvalidOrderData("Monto inválido")

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise InvalidOrderData("Monedas distintas")
        return Money(self.amount + other.amount, self.currency)


@dataclass(frozen=True)
class OrderItem:
    sku: str
    quantity: int
    unit_price: Money

    def __post_init__(self):
        if not self.sku.strip() or self.quantity <= 0:
            raise InvalidOrderData("Artículo inválido")

    @property
    def subtotal(self) -> Money:
        return Money(self.unit_price.amount * self.quantity, self.unit_price.currency)


# ------------------------------------------------------------------- Entidades
@dataclass(frozen=True)
class Customer:
    id: str
    is_vip: bool = False
    active: bool = True


class OrderStatus(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"


@dataclass(frozen=True)
class DomainEvent:
    """Hecho ya ocurrido: inmutable y con marca de tiempo."""
    name: str
    order_id: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    data: dict = field(default_factory=dict, compare=False)


@dataclass
class Order:
    """Aggregate Root: concentra invariantes y máquina de estados."""
    customer: Customer
    id: str
    has_promotion: bool = False
    status: OrderStatus = OrderStatus.DRAFT
    items: list = field(default_factory=list)
    events: list = field(default_factory=list)

    # --- consultas
    @property
    def units(self) -> int:
        return sum(item.quantity for item in self.items)

    @property
    def total(self) -> Money:
        amount = sum((x.subtotal.amount for x in self.items), Decimal("0"))
        return Money(amount)

    # --- comportamiento
    def add_item(self, item: OrderItem) -> None:
        if self.status != OrderStatus.DRAFT:
            raise InvalidOrderTransition("Solo DRAFT admite artículos")
        if item.unit_price.currency != "MXN":
            raise InvalidOrderData("Solo MXN")
        if self.units + item.quantity > MAX_UNITS:
            raise OrderItemLimitExceeded("Máximo 20 unidades")
        self.items.append(item)

    def _record(self, name: str, **data) -> None:
        self.events.append(DomainEvent(name, self.id, data=data))

    def _require_status(self, expected: OrderStatus, action: str) -> None:
        if self.status != expected:
            raise InvalidOrderTransition(
                f"No se puede {action} un pedido en estado {self.status.value}"
            )

    # Regla general: validar -> cambiar estado -> registrar evento.
    def confirm(self) -> None:
        self._require_status(OrderStatus.DRAFT, "confirmar")
        if not self.items or not self.customer.active:
            raise InvalidOrderData("Requiere artículos y cliente activo")
        self.status = OrderStatus.CONFIRMED
        self._record("OrderConfirmed", customer_id=self.customer.id,
                     total=self.total.amount)

    def ship(self, tracking_number: str) -> None:
        self._require_status(OrderStatus.CONFIRMED, "enviar")
        if not tracking_number or not tracking_number.strip():
            raise InvalidOrderData("El envío requiere número de guía")
        self.status = OrderStatus.SHIPPED
        self._record("OrderShipped", tracking_number=tracking_number.strip())

    def cancel(self, reason: str) -> None:
        self._require_status(OrderStatus.CONFIRMED, "cancelar")
        if not reason or not reason.strip():
            raise InvalidOrderData("La cancelación requiere un motivo")
        self.status = OrderStatus.CANCELLED
        self._record("OrderCancelled", reason=reason.strip())

    def deliver(self) -> None:
        self._require_status(OrderStatus.SHIPPED, "entregar")
        self.status = OrderStatus.DELIVERED
        self._record("OrderDelivered")

    def return_order(self) -> None:
        self._require_status(OrderStatus.SHIPPED, "devolver")
        self.status = OrderStatus.RETURNED
        self._record("OrderReturned")
