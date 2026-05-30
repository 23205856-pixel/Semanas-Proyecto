# Test de Regresión Cruzada — EcoMarket

---

# TC-X1 — SSE activo + Circuit Breaker transiciona a ABIERTO

## Setup

- ClienteSSEMultiplex conectado.
- ClienteRobusto conectado al mock server.
- Mock configurado inicialmente en modo normal.
- CircuitBreaker configurado con umbral de 5 fallos.

## Acción

- Mantener activo el stream SSE.
- Simultáneamente provocar 5 respuestas HTTP 503 consecutivas.

## Verificación

- El stream SSE continúa procesando eventos.
- El EventRouter sigue despachando eventos.
- El Circuit Breaker HTTP transiciona a ABIERTO.
- El SSE no se desconecta.

## Resultado Observable

```txt
[CB] Estado actual: ABIERTO
[SSE] Evento recibido: {'producto_id': 'P1', 'precio_nuevo': 99}
[SSE] Eventos procesados: 1