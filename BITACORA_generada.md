# Bitácora de escenarios E01–E15

| Caso | Pedido | Estado inicial | Operación | Resultado real | Estado final | Eventos | Objetivo |
|---|---|---|---|---|---|---|---|
| E01 | O001 | DRAFT | evaluar_descuento | evaluar descuento -> OK (10%) | DRAFT | (ninguno) | 10% |
| E02 | O002 | DRAFT | evaluar_descuento | evaluar descuento -> OK (0%) | DRAFT | (ninguno) | 0% |
| E03 | O003 | DRAFT | confirmar | confirm() -> InvalidOrderData: Requiere artículos y cliente activo | DRAFT | (ninguno) | rechazo |
| E04 | O005 | DRAFT | evaluar_descuento | evaluar descuento -> OK (0%) | DRAFT | (ninguno) | 0% |
| E05 | O006 | DRAFT | evaluar_descuento | evaluar descuento -> OK (5%) | DRAFT | (ninguno) | 5% |
| E06 | O007 | DRAFT | confirmar | confirm() -> InvalidOrderData: Requiere artículos y cliente activo | DRAFT | (ninguno) | rechazo |
| E07 | O008 | DRAFT | confirmar | confirm() -> OK | CONFIRMED | OrderConfirmed | exito |
| E08 | O009 | DRAFT | agregar SKU003 x2 | add_item(SKU003 x2) -> OrderItemLimitExceeded: Máximo 20 unidades | DRAFT | (ninguno) | rechazo |
| E09 | O010 | DRAFT | evaluar_descuento | evaluar descuento -> OK (0%) | DRAFT | (ninguno) | 0% |
| E10 | O011 | DRAFT | evaluar_descuento | evaluar descuento -> OK (0%) | DRAFT | (ninguno) | 0% |
| E11 | O012 | DRAFT | confirmar y enviar sin guia | confirm() -> OK<br>ship('') -> InvalidOrderData: El envío requiere número de guía | CONFIRMED | OrderConfirmed | rechazo envio |
| E12 | O013 | DRAFT | confirmar dos veces | confirm() #1 -> OK<br>confirm() #2 -> InvalidOrderTransition: No se puede confirmar un pedido en estado CONFIRMED | CONFIRMED | OrderConfirmed | rechazo segunda |
| E13 | O014 | DRAFT | confirmar, enviar y cancelar | confirm() -> OK<br>ship('GUIA-001') -> OK<br>cancel('cambio de opinion') -> InvalidOrderTransition: No se puede cancelar un pedido en estado SHIPPED | SHIPPED | OrderConfirmed, OrderShipped | rechazo cancelacion |
| E14 | O015 | DRAFT | confirmar, enviar y devolver | confirm() -> OK<br>ship('GUIA-002') -> OK<br>return_order() -> OK | RETURNED | OrderConfirmed, OrderShipped, OrderReturned | exito (RETURNED) |
| E15 | O016 | DRAFT | confirmar, enviar y entregar | confirm() -> OK<br>ship('GUIA-003') -> OK<br>deliver() -> OK | DELIVERED | OrderConfirmed, OrderShipped, OrderDelivered | exito (DELIVERED) |
