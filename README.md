# TechStore U4 – Núcleo de negocio de pedidos

Actividad 4 · Componentes de Lógica de Negocio · FIME UANL.
Entidades/Value Objects, Specification Pattern, máquina de estados con Domain Events y API REST (FastAPI). Todo en memoria (no persiste).

## Instalación
```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1   |  macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Ejecución
```bash
python cargar_csv.py        # carga los 16 pedidos (todos DRAFT)
python escenarios.py        # ejecuta E01–E15
python -m pytest -q         # pruebas
uvicorn app.api:app --reload   # API; docs en http://127.0.0.1:8000/docs
```

## Estructura
```
app/domain.py          Money, OrderItem, Customer, Order, DomainEvent, excepciones
app/specifications.py  Specification, And/Or/Not, reglas y política de descuento
app/api.py             Controladores delgados + traducción de excepciones a HTTP
tests/                 test_domain, test_specifications, test_api
datos/                 CSV del paquete
BITACORA.md            Resultado de E01–E15
```

## Reglas
- Money: Decimal, sin negativos, sin float. Máximo 20 **unidades** por pedido.
- Descuento 10 %: VIP, total > 500, ≥ 4 unidades, sin promoción. Descuento 5 %: total > 5000, sin promoción. Prioridad 10 %.
- Confirmar: solo DRAFT, con artículos y cliente activo. Enviar: solo CONFIRMED y con guía. Cancelar: solo CONFIRMED y con motivo. Entregar/devolver: solo SHIPPED.

## Endpoints
| Método | Ruta | Éxito | Errores |
|---|---|---|---|
| GET | /orders/{id} | 200 | 404 |
| GET | /orders/{id}/discount | 200 | 404 |
| POST | /orders/{id}/confirm | 200 | 404, 409 (estado), 422 (vacío/inactivo) |
| POST | /orders/{id}/ship  `{"tracking_number": "..."}` | 200 | 404, 409, 422 |
| POST | /orders/{id}/cancel  `{"reason": "..."}` | 200 | 404, 409, 422 |
| POST | /orders/{id}/deliver | 200 | 404, 409 |
| POST | /orders/{id}/return | 200 | 404, 409 |

409 = `InvalidOrderTransition`; 422 = `InvalidOrderData` / `OrderItemLimitExceeded`.
