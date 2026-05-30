
---

# contribucion_equipo.md

```md
# Contribución del Equipo

## Integrante

- Rafael Gil Samaniego Vazquez

---

# Distribución de Trabajo

El proyecto fue desarrollado individualmente.

Las siguientes actividades fueron realizadas por el único integrante:

- Diseño del Circuit Breaker
- Implementación de ClienteRobusto
- Implementación de ClienteSSEMultiplex
- Integración JWT + refresh token
- Implementación de EventRouter
- Automatización de pruebas con pytest
- Implementación de regresión cruzada
- Mock server para simulación de fallos
- Validación de invariantes
- Integración SSE + resiliencia
- Documentación técnica
- ADR y bitácora IA

---

# Defensa Breve

El proyecto fue construido siguiendo principios de resiliencia y desacoplamiento.

Las decisiones más importantes fueron:

- Separar el estado del Circuit Breaker del TokenManager.
- Mantener el SSE desacoplado del tráfico HTTP protegido por el breaker.
- Implementar refresh singleton para evitar tormentas de refresh concurrentes.
- Utilizar pruebas automatizadas para validar invariantes críticos.

El sistema final permite:

- Recuperación automática.
- Tolerancia a fallos 5xx.
- Reconexión SSE.
- Fail-fast controlado.
- Protección ante concurrencia.

El comportamiento fue validado mediante:
- pytest
- pruebas concurrentes
- simulaciones de fallo
- mocks reproducibles
- escenarios de regresión cruzada