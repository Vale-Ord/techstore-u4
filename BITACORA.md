# Bitácora de escenarios E01–E15

Resultados obtenidos con `python escenarios.py` (fixtures recargados en cada caso).
Reglas: 10 % = VIP + total > 500 + ≥ 4 unidades + sin promoción; 5 % = total > 5000 + sin promoción; prioridad 10 %.

| Caso | Pedido | Precondiciones | Operación | Resultado real | Evento | Prueba |
|---|---|---|---|---|---|---|
| E01 | O001 | C001 VIP activo, 4 u, 2,100.00, sin promo, DRAFT | evaluar descuento | **10 %** (210.00; neto 1,890.00) | ninguno (solo consulta) | `test_specifications::test_tasa_de_descuento[O001]` |
| E02 | O002 | C002 no VIP, 2 u, 1,050.00, sin promo | evaluar descuento | **0 %** (no VIP y total < 5000) | ninguno | `test_tasa_de_descuento[O002]` |
| E03 | O003 | C003 VIP **inactivo**, 4 u, 2,100.00 | `confirm()` | **Rechazo** `InvalidOrderData`; sigue DRAFT | ninguno | `test_domain::test_confirmar_cliente_inactivo` / API 422 |
| E04 | O005 | C005 VIP, 4 u, 2,100.00, **promo activa** | evaluar descuento | **0 %** (la promoción bloquea ambas reglas) | ninguno | `test_tasa_de_descuento[O005]` |
| E05 | O006 | C006 no VIP, 1 u (laptop), 18,000.00, sin promo | evaluar descuento | **5 %** (900.00; neto 17,100.00) | ninguno | `test_tasa_de_descuento[O006]` |
| E06 | O007 | C007, **sin artículos** | `confirm()` | **Rechazo** `InvalidOrderData`; sigue DRAFT | ninguno | `test_confirmar_pedido_vacio` / API 422 |
| E07 | O008 | C008 activo, 20 u exactas (SKU003 × 20), 2,400.00 | `confirm()` | **Éxito**: DRAFT → CONFIRMED | `OrderConfirmed` | `test_20_unidades_exactas_permitidas`, `test_confirmar_exito_registra_evento` |
| E08 | O009 | 19 u (2,280.00) | `add_item(SKU003 × 2)` | **Rechazo** `OrderItemLimitExceeded` (21 > 20); el pedido queda con 19 u | ninguno | `test_21_unidades_rechazadas_sin_modificar_pedido` |
| E09 | O010 | C010 no VIP, 2 u, total **exactamente 500.00** | evaluar descuento | **0 %** (umbral estricto `>`; además no es VIP) | ninguno | `test_umbral_500_es_estricto` |
| E10 | O011 | C011 VIP, **3 u**, 1,500.00 | evaluar descuento | **0 %** (requiere ≥ 4 u) | ninguno | `test_minimo_4_unidades` |
| E11 | O012 | C012 activo, 1 u, 850.00 | `confirm()` y luego `ship("")` | Confirmar OK; envío **rechazado** (`InvalidOrderData`, falta guía); queda CONFIRMED | solo `OrderConfirmed` | `test_envio_sin_guia` / API 422 |
| E12 | O013 | C001 activo, 1 u, 600.00 | `confirm()` ×2 | 1.ª OK (CONFIRMED); 2.ª **rechazo** `InvalidOrderTransition` | un solo `OrderConfirmed` | `test_confirmacion_doble_no_duplica_evento` / API 409 |
| E13 | O014 | C002 activo, 1 u, 600.00 | `confirm()`, `ship("GUIA-001")`, `cancel(motivo)` | Confirmar y enviar OK; cancelar **rechazado** `InvalidOrderTransition`; queda SHIPPED | `OrderConfirmed`, `OrderShipped` (sin `OrderCancelled`) | `test_cancelacion_desde_shipped_rechazada` / API 409 |
| E14 | O015 | C005 activo, 1 u, 450.00 | `confirm()`, `ship("GUIA-002")`, `return_order()` | **Éxito**: termina en RETURNED | `OrderConfirmed`, `OrderShipped`, `OrderReturned` | `test_devolucion_y_entrega_validas` |
| E15 | O016 | C007 activo, 1 u, 2,100.00 | `confirm()`, `ship("GUIA-003")`, `deliver()` | **Éxito**: termina en DELIVERED | `OrderConfirmed`, `OrderShipped`, `OrderDelivered` | `test_devolucion_y_entrega_validas` |

## Diagrama de estados

```
DRAFT --confirm--> CONFIRMED --ship(guía)--> SHIPPED --deliver--> DELIVERED
                       |                        |
                  cancel(motivo)             return
                       |                        |
                   CANCELLED                RETURNED
```

Cualquier otra combinación estado/operación lanza `InvalidOrderTransition` (HTTP 409) y no cambia el estado ni agrega eventos.
Precondiciones que fallan lanzan `InvalidOrderData` (HTTP 422).

## Domain Events

| Evento | Se registra cuando | Datos |
|---|---|---|
| OrderConfirmed | confirm() válido | customer_id, total |
| OrderShipped | ship() con guía | tracking_number |
| OrderCancelled | cancel() con motivo | reason |
| OrderDelivered | deliver() desde SHIPPED | — |
| OrderReturned | return_order() desde SHIPPED | — |

Todos se agregan **al final** de la operación, después de validar y cambiar el estado.
