## Interacción 1 — Revisión del ADR

### Prompt usado

Actúa como comité de revisión arquitectónica.

Mi ADR:
Título: Breaker separado para autenticación

Contexto:
El cliente EcoMarket utiliza un CircuitBreaker para proteger llamadas HTTP
contra fallos consecutivos del backend. Los endpoints de autenticación
(/auth/login y /auth/refresh) tienen comportamiento crítico diferente al
resto de endpoints de negocio.

Decisión:
Decidimos no compartir el mismo CircuitBreaker entre autenticación y
peticiones normales de inventario.

Consecuencias positivas:
- Un fallo temporal del endpoint de inventario no bloquea automáticamente
  la renovación del token.
- El sistema puede recuperar autenticación aunque otros endpoints sigan
  degradados o saturados.

Consecuencias negativas:
- Aumenta la complejidad de configuración y monitoreo porque existen
  múltiples breakers.
- Puede producir tráfico adicional hacia autenticación durante incidentes
  parciales del sistema.

Escenario adverso:
Esta decisión sería incorrecta si el servidor de autenticación comparte
exactamente la misma infraestructura degradada que el resto de la API,
porque múltiples breakers permitirían seguir enviando tráfico a un sistema
ya saturado.

### Respuesta resumida de la IA

La IA planteó un escenario donde el backend de autenticación y el backend
de inventario comparten infraestructura física o balanceadores. En ese caso,
tener breakers separados puede provocar que el cliente continúe enviando
peticiones de autenticación mientras el sistema ya se encuentra degradado,
incrementando la carga durante la recuperación.

### Decisión aceptada o rechazada

Aceptada.

### Justificación técnica

La observación identifica correctamente el trade-off principal de la decisión:
aislamiento de fallos frente a incremento potencial de tráfico durante
incidentes parciales. El análisis es consistente con arquitecturas
distribuidas donde múltiples servicios dependen de recursos compartidos.