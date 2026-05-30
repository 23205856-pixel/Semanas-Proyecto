## Interacción 1

### Prompt usado

Actúa como comité de revisión arquitectónica.

Mi ADR:
Título: Breaker separado para autenticación
Contexto: El cliente EcoMarket utiliza un CircuitBreaker para proteger
llamadas HTTP contra fallos consecutivos del backend. Los endpoints de
autenticación tienen comportamiento crítico diferente al resto de endpoints.

Decisión: Decidimos no compartir el mismo CircuitBreaker entre autenticación
y peticiones normales de inventario.

Consecuencias +:
- Un fallo temporal del endpoint de inventario no bloquea la renovación
  del token.
- El sistema puede recuperar autenticación aunque otros endpoints sigan
  degradados.

Consecuencias −:
- Mayor complejidad operativa.
- Posible tráfico adicional hacia autenticación durante incidentes.

Escenario adverso:
La decisión sería incorrecta si autenticación comparte exactamente la misma
infraestructura degradada que el resto de la API.

### Respuesta resumida de la IA

La IA presentó un escenario donde múltiples breakers podían seguir enviando
tráfico a un backend compartido ya saturado, empeorando la degradación.

### Decisión aceptada o rechazada

Aceptada.

### Justificación técnica

El escenario confirma el trade-off identificado en el ADR: aislamiento de
fallos versus aumento de tráfico durante incidentes parciales. La observación
es consistente con sistemas distribuidos donde autenticación e inventario
dependen de infraestructura compartida.