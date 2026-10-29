"""Specification Pattern: reglas de elegibilidad de descuentos.

Las Specifications SOLO evalúan; nunca modifican el pedido.
"""
from decimal import Decimal

from app.domain import Money, Order


class Specification:
    def is_satisfied_by(self, order: Order) -> bool:
        raise NotImplementedError

    def __and__(self, other):
        return AndSpec(self, other)

    def __or__(self, other):
        return OrSpec(self, other)

    def __invert__(self):
        return NotSpec(self)


class AndSpec(Specification):
    def __init__(self, left, right):
        self.left, self.right = left, right

    def is_satisfied_by(self, order):
        return self.left.is_satisfied_by(order) and self.right.is_satisfied_by(order)


class OrSpec(Specification):
    def __init__(self, left, right):
        self.left, self.right = left, right

    def is_satisfied_by(self, order):
        return self.left.is_satisfied_by(order) or self.right.is_satisfied_by(order)


class NotSpec(Specification):
    def __init__(self, spec):
        self.spec = spec

    def is_satisfied_by(self, order):
        return not self.spec.is_satisfied_by(order)


class MinimumAmountSpec(Specification):
    """Total ESTRICTAMENTE mayor al umbral (>)."""
    def __init__(self, threshold: Decimal):
        self.threshold = threshold

    def is_satisfied_by(self, order):
        return order.total.amount > self.threshold


class VIPCustomerSpec(Specification):
    def is_satisfied_by(self, order):
        return order.customer.is_vip


class MinimumUnitsSpec(Specification):
    """Al menos N unidades (>=), sumando cantidades, no renglones."""
    def __init__(self, minimum: int):
        self.minimum = minimum

    def is_satisfied_by(self, order):
        return order.units >= self.minimum


class ActivePromotionSpec(Specification):
    def is_satisfied_by(self, order):
        return order.has_promotion


class ActiveCustomerSpec(Specification):
    """Quinta regla opcional: el cliente puede operar."""
    def is_satisfied_by(self, order):
        return order.customer.active


# --------------------------------------------------------- Política de descuento
TEN_PERCENT = (
    MinimumAmountSpec(Decimal("500"))
    & VIPCustomerSpec()
    & MinimumUnitsSpec(4)
    & ~ActivePromotionSpec()
)
FIVE_PERCENT = MinimumAmountSpec(Decimal("5000")) & ~ActivePromotionSpec()
ANY_DISCOUNT = TEN_PERCENT | FIVE_PERCENT  # composición con OR


def discount_rate(order: Order) -> Decimal:
    """Prioridad: 10 % sobre 5 % cuando se cumplen ambas."""
    if not ANY_DISCOUNT.is_satisfied_by(order):
        return Decimal("0")
    if TEN_PERCENT.is_satisfied_by(order):
        return Decimal("0.10")
    return Decimal("0.05")


def discount_amount(order: Order) -> Money:
    return Money(order.total.amount * discount_rate(order))


def total_with_discount(order: Order) -> Money:
    return Money(order.total.amount - discount_amount(order).amount)
