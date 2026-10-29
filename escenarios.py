"""Ejecuta E01-E15 y genera BITACORA.md con el resultado REAL de cada caso.

Uso: python escenarios.py
Cada escenario carga fixtures frescos, así que no se contaminan entre sí.
"""
from decimal import Decimal

from app.domain import DomainException, OrderItem, Money
from app.specifications import discount_rate
from cargar_csv import load_fixture


def run(pid, steps):
    """Ejecuta pasos [(nombre, callable)] y devuelve (estado_ini, ops, resultado, eventos)."""
    order = load_fixture()[pid]
    ini = order.status.value
    log = []
    for label, fn in steps:
        try:
            out = fn(order)
            log.append(f"{label} -> OK" + (f" ({out})" if out is not None else ""))
        except DomainException as exc:
            log.append(f"{label} -> {type(exc).__name__}: {exc}")
    evs = [e.name for e in order.events] or ["(ninguno)"]
    return order, ini, log, evs


def disc(o):
    return f"{int(discount_rate(o) * 100)}%"


ESC = [
    ("E01", "O001", "evaluar_descuento", [("evaluar descuento", disc)], "10%"),
    ("E02", "O002", "evaluar_descuento", [("evaluar descuento", disc)], "0%"),
    ("E03", "O003", "confirmar", [("confirm()", lambda o: o.confirm())], "rechazo"),
    ("E04", "O005", "evaluar_descuento", [("evaluar descuento", disc)], "0%"),
    ("E05", "O006", "evaluar_descuento", [("evaluar descuento", disc)], "5%"),
    ("E06", "O007", "confirmar", [("confirm()", lambda o: o.confirm())], "rechazo"),
    ("E07", "O008", "confirmar", [("confirm()", lambda o: o.confirm())], "exito"),
    ("E08", "O009", "agregar SKU003 x2",
     [("add_item(SKU003 x2)",
       lambda o: o.add_item(OrderItem("SKU003", 2, Money(Decimal("120.00")))))], "rechazo"),
    ("E09", "O010", "evaluar_descuento", [("evaluar descuento", disc)], "0%"),
    ("E10", "O011", "evaluar_descuento", [("evaluar descuento", disc)], "0%"),
    ("E11", "O012", "confirmar y enviar sin guia",
     [("confirm()", lambda o: o.confirm()), ("ship('')", lambda o: o.ship(""))], "rechazo envio"),
    ("E12", "O013", "confirmar dos veces",
     [("confirm() #1", lambda o: o.confirm()), ("confirm() #2", lambda o: o.confirm())],
     "rechazo segunda"),
    ("E13", "O014", "confirmar, enviar y cancelar",
     [("confirm()", lambda o: o.confirm()), ("ship('GUIA-001')", lambda o: o.ship("GUIA-001")),
      ("cancel('cambio de opinion')", lambda o: o.cancel("cambio de opinion"))],
     "rechazo cancelacion"),
    ("E14", "O015", "confirmar, enviar y devolver",
     [("confirm()", lambda o: o.confirm()), ("ship('GUIA-002')", lambda o: o.ship("GUIA-002")),
      ("return_order()", lambda o: o.return_order())], "exito (RETURNED)"),
    ("E15", "O016", "confirmar, enviar y entregar",
     [("confirm()", lambda o: o.confirm()), ("ship('GUIA-003')", lambda o: o.ship("GUIA-003")),
      ("deliver()", lambda o: o.deliver())], "exito (DELIVERED)"),
]

if __name__ == "__main__":
    lines = ["# Bitácora de escenarios E01–E15", "",
             "| Caso | Pedido | Estado inicial | Operación | Resultado real | Estado final | Eventos | Objetivo |",
             "|---|---|---|---|---|---|---|---|"]
    for cid, pid, accion, steps, objetivo in ESC:
        order, ini, log, evs = run(pid, steps)
        lines.append(f"| {cid} | {pid} | {ini} | {accion} | {'<br>'.join(log)} | "
                     f"{order.status.value} | {', '.join(evs)} | {objetivo} |")
        print(cid, pid, ini, "|", " ; ".join(log), "| final:", order.status.value, "| eventos:", evs)
    open("BITACORA_generada.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
