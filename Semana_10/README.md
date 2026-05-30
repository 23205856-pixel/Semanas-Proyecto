# EcoMarket Client — Hito 2
# Cliente Resiliente + Circuit Breaker + SSE + JWT

Proyecto final de Programación del Lado Cliente.

Implementación completa de resiliencia cliente para EcoMarket utilizando:

- Circuit Breaker
- JWT + Refresh Token
- SSE Multiplexado
- Cliente HTTP resiliente
- Reconexión SSE
- Tests automatizados
- Mock server para pruebas
- Regresión cruzada
- Pruebas concurrentes
- Logging resiliente
- Fail Fast
- Singleton Refresh
- Timeout Recovery
- EventRouter
- Protección concurrente
- Mocking HTTP
- Integración SSE + JWT + Circuit Breaker

---

# Autores

- Rafael Gil Samaniego Vázquez
- Benjamin Villaseñor Casian

---

# Materia

Programación del Lado Cliente

---

# Entrega

Semana 10 — Hito 2  
Cliente Resiliente EcoMarket

---

# Hito Implementado

## Hito 2 — Cliente Resiliente

Se implementó un cliente robusto capaz de:

- Detectar fallos del backend
- Abrir y cerrar circuitos automáticamente
- Recuperarse tras fallos temporales
- Mantener streams SSE activos
- Manejar JWT y refresh token
- Proteger refresh concurrentes
- Notificar eventos a UI
- Ejecutar pruebas automatizadas de invariantes
- Ejecutar pruebas de regresión cruzada
- Mantener conexiones SSE persistentes
- Reconectarse usando Last-Event-ID
- Separar responsabilidades entre módulos
- Aplicar tolerancia a fallos
- Evitar sobrecargar el backend
- Simular fallos HTTP reales
- Validar escenarios concurrentes

---

# Objetivo del Proyecto

Construir un cliente resiliente para EcoMarket capaz de:

- Resistir fallos del backend
- Recuperarse automáticamente
- Mantener conexiones SSE activas
- Administrar autenticación JWT
- Evitar cascadas de fallos
- Soportar concurrencia
- Garantizar estabilidad cliente-servidor

---

# Tecnologías Utilizadas

| Tecnología | Uso |
|---|---|
| Python 3.12 | Lenguaje principal |
| asyncio | Concurrencia |
| aiohttp | HTTP async + mock server |
| pytest | Testing |
| pytest-asyncio | Tests async |
| SSE | Eventos en tiempo real |
| JWT | Autenticación |
| PowerShell | Ejecución |
| VSCode | Desarrollo |

---

# Versiones Utilizadas

## Python

```powershell
python --version
```

Resultado esperado:

```powershell
Python 3.12.10
```

---

## pip

```powershell
pip --version
```

Resultado esperado:

```powershell
pip 25.x
```

---

## pytest

```powershell
pytest --version
```

Resultado esperado:

```powershell
pytest 9.x
```

---

# Estructura Completa del Proyecto

```text
Semana_10/
│
├── Docs/
│   ├── adr_decision_critica.md
│   ├── autopsia_bugs.md
│   ├── bitacora_ia.md
│   ├── checklist_invariantes.md
│   ├── tc_cross_regression.md
│   └── contribucion_equipo.md
│
├── ecomarket-client/
│
│   ├── cliente/
│   │
│   │   ├── circuit_breaker.py
│   │   ├── cliente_integrado.py
│   │   ├── cliente_robusto.py
│   │   ├── cliente_sse_multiplex.py
│   │   ├── token_manager.py
│   │   ├── demo_resiliencia.py
│   │   ├── demo_resiliencia.log
│   │   ├── test_circuit_breaker.py
│   │   ├── test_tc_x1.py
│   │   ├── test_tc_x2.py
│   │   └── test_tc_x3.py
│
│   ├── mock/
│   │   ├── mock_ecomarket.py
│   │   └── mock_server.py
│
│   ├── .venv/
│   └── README.md
│
└── semana10_cliente_aetl_ver2.html
```

---

# Requisitos

## Requisitos de software

- Windows 10/11
- Python 3.12+
- pip
- PowerShell
- VSCode recomendado
- Terminal con permisos de ejecución

---

# Instalación del Proyecto

---

## 1. Crear carpeta del proyecto

Ruta sugerida:

```text
C:\dev\ecomarket-client
```

---

## 2. Abrir PowerShell

Ejecutar:

```powershell
cd C:\dev\ecomarket-client
```

---

## 3. Crear entorno virtual

Comando:

```powershell
python -m venv .venv
```

Resultado esperado:

```text
Se crea carpeta .venv
```

---

## 4. Activar entorno virtual

Comando:

```powershell
.\.venv\Scripts\Activate.ps1
```

Resultado esperado:

```powershell
(.venv) PS C:\dev\ecomarket-client>
```

---

# Instalación de Dependencias

---

## Instalar aiohttp

```powershell
pip install aiohttp
```

Resultado esperado:

```text
Successfully installed aiohttp
```

---

## Instalar pytest

```powershell
pip install pytest
```

Resultado esperado:

```text
Successfully installed pytest
```

---

## Instalar pytest-asyncio

```powershell
pip install pytest-asyncio
```

Resultado esperado:

```text
Successfully installed pytest-asyncio
```

---

# Arquitectura Implementada

El proyecto está dividido en módulos desacoplados:

| Módulo | Responsabilidad |
|---|---|
| CircuitBreaker | Tolerancia a fallos |
| TokenManager | JWT y refresh |
| ClienteRobusto | HTTP resiliente |
| ClienteSSEMultiplex | Eventos SSE |
| EventRouter | Routing de eventos |
| MockServer | Simulación backend |

---

# Componentes Implementados

---

# 1. Circuit Breaker

## Archivo

```text
cliente/circuit_breaker.py
```

## Funciones principales

- Estado CERRADO
- Estado ABIERTO
- Estado SEMIABIERTO
- Conteo de fallos consecutivos
- Timeout automático
- Fail fast
- Protección concurrente en semiabierto
- Recuperación automática
- Exclusión de errores cliente

---

# 2. Token Manager

## Archivo

```text
cliente/token_manager.py
```

## Funciones

- Gestión JWT
- Refresh token
- Singleton refresh
- Auth header
- Logout
- Expiración de token
- Refresh concurrente protegido

---

# 3. Cliente Robusto

## Archivo

```text
cliente/cliente_robusto.py
```

## Funciones

- Requests HTTP resilientes
- Integración CB
- Refresh automático
- Retry controlado
- Manejo 401/403/5xx
- Observer UI
- Fail Fast

---

# 4. Cliente SSE Multiplex

## Archivo

```text
cliente/cliente_sse_multiplex.py
```

## Funciones

- Multiplexación SSE
- EventRouter
- Reconexión
- Last-Event-ID
- Streams simulados
- Handlers por tipo
- Eventos concurrentes

---

# 5. Mock Server

## Archivo

```text
mock/mock_server.py
```

## Simula

- HTTP 200
- HTTP 503
- HTTP 401
- Timeout
- Refresh token
- Backend resiliente

---

# Ejecución Completa del Proyecto

---

# PASO 1 — Activar entorno virtual

Ruta:

```powershell
cd C:\dev\ecomarket-client
```

Comando:

```powershell
.\.venv\Scripts\Activate.ps1
```

Resultado esperado:

```powershell
(.venv) PS C:\dev\ecomarket-client>
```

---

# PASO 2 — Ejecutar Mock Server

Archivo:

```text
mock/mock_server.py
```

Ruta:

```powershell
cd C:\dev\ecomarket-client\mock
```

Comando:

```powershell
python .\mock_server.py
```

Resultado esperado:

```text
[MOCK] Servidor activo en http://localhost:9000
```

---

# PASO 3 — Ejecutar Mock EcoMarket

Archivo:

```text
mock/mock_ecomarket.py
```

Ruta:

```powershell
cd C:\dev\ecomarket-client\mock
```

Comando:

```powershell
python .\mock_ecomarket.py
```

Resultado esperado:

```text
[MOCK] EcoMarket en http://localhost:8888
```

---

# PASO 4 — Ejecutar Cliente SSE

Archivo:

```text
cliente/cliente_sse_multiplex.py
```

Ruta:

```powershell
cd C:\dev\ecomarket-client\cliente
```

Comando:

```powershell
python .\cliente_sse_multiplex.py
```

Resultado esperado:

```text
[ALERTA] Cambio mayor al 5%
[CRITICO] Stock muy bajo
```

---

# PASO 5 — Ejecutar Cliente Integrado

Archivo:

```text
cliente/cliente_integrado.py
```

Ruta:

```powershell
cd C:\dev\ecomarket-client\cliente
```

Comando:

```powershell
python .\cliente_integrado.py
```

Resultado esperado:

```text
[LOGIN] Token almacenado · rol=viewer
[HTTP #1] 200
[HTTP #2] 200
[HTTP #3] 200
[HTTP #4] 503
[BREAKER] Fail fast
Estado final: circuito=CERRADO
```

---

# PASO 6 — Ejecutar Demo Resiliencia

Archivo:

```text
cliente/demo_resiliencia.py
```

Ruta:

```powershell
cd C:\dev\ecomarket-client\cliente
```

Comando:

```powershell
python .\demo_resiliencia.py
```

Resultado esperado:

```text
=== ESCENARIO 1: RESPUESTAS 200 ===

[HTTP #1] 200
[HTTP #2] 200

=== ESCENARIO 2: FALLAS 503 ===

[HTTP ERROR] HTTP 503
[UI] Circuito ABIERTO
[BREAKER] OPEN

=== ESCENARIO 3: RECUPERACION ===

[RECOVERY] 200
Estado final → CB=CERRADO
```

---

# Archivo de Evidencia

## Archivo

```text
cliente/demo_resiliencia.log
```

## Contiene

- Fallos HTTP
- Eventos UI
- Recuperación
- Apertura circuito
- Cierre circuito
- Logs resiliencia

---

# Tests Automatizados

---

# Ejecutar Tests Invariantes

Archivo:

```text
cliente/test_circuit_breaker.py
```

Ruta:

```powershell
cd C:\dev\ecomarket-client\cliente
```

Comando:

```powershell
pytest test_circuit_breaker.py -v
```

Resultado esperado:

```text
6 passed
```

---

# Invariantes Validados

| Invariante | Resultado |
|---|---|
| INV-A1 | PASS |
| INV-A2 | PASS |
| INV-A3 | PASS |
| INV-A4 | PASS |
| INV-B1 | PASS |
| INV-B2 | PASS |
| INV-B3 | PASS |

---

# Explicación de Invariantes

| Código | Descripción |
|---|---|
| INV-A1 | CB no accede payload JWT |
| INV-A2 | Solo 1 request en SEMIABIERTO |
| INV-A3 | Reset fallos al cerrar |
| INV-A4 | 401/403 no abren CB |
| INV-B1 | TokenManager desacoplado |
| INV-B2 | Tokens no aparecen logs |
| INV-B3 | Refresh singleton |

---

# Tests Regresión Cruzada

---

# TC-X1

## Archivo

```text
cliente/test_tc_x1.py
```

## Comando

```powershell
python .\test_tc_x1.py
```

## Verifica

- SSE continúa funcionando mientras CB está ABIERTO

## Resultado esperado

```text
OK → El SSE continuó funcionando mientras el Circuit Breaker HTTP estaba ABIERTO.
```

---

# TC-X2

## Archivo

```text
cliente/test_tc_x2.py
```

## Comando

```powershell
pytest test_tc_x2.py -v
```

## Verifica

- Refresh singleton
- CB en SEMIABIERTO
- Concurrencia

## Resultado esperado

```text
1 passed
```

---

# TC-X3

## Archivo

```text
cliente/test_tc_x3.py
```

## Comando

```powershell
python .\test_tc_x3.py
```

## Verifica

- Reconexión SSE
- Last-Event-ID
- Persistencia de estado

## Resultado esperado

```text
OK → Reconexión SSE conserva Last-Event-ID correctamente.
```

---

# Historial de Desarrollo

---

# Fase 1

- Implementación Circuit Breaker
- Estados base
- Timeout recovery

---

# Fase 2

- SSE Multiplexado
- EventRouter
- Reconexión

---

# Fase 3

- JWT
- Refresh Token
- ClienteRobusto

---

# Fase 4

- Mock server resiliente
- HTTP 503
- HTTP 401
- Timeout

---

# Fase 5

- Tests automatizados
- pytest
- pytest-asyncio

---

# Fase 6

- Regresión cruzada
- Integración completa

---

# Fase 7

- Demo resiliencia
- Logging
- Evidencias

---

# Problemas Encontrados

---

# Error WinError 10013

Problema:

```text
PermissionError: [WinError 10013]
```

Solución:

- Cambio puerto 8080 → 8888

---

# Error coroutine object is not callable

Problema:

```text
'coroutine' object is not callable
```

Solución:

- Corregir llamada CB.ejecutar()

---

# Error ModuleNotFoundError

Problema:

```text
No module named 'mock'
```

Solución:

- Corregir imports relativos

---

# Decisiones Arquitectónicas

---

# Circuit Breaker separado TokenManager

Razón:

- Bajo acoplamiento
- SRP
- Testing sencillo

---

# SSE separado del CB

Razón:

- SSE usa TCP persistente
- CB solo HTTP request-response

---

# Distribución del Trabajo

## Rafael Gil Samaniego Vázquez

- Circuit Breaker
- ClienteRobusto
- Mock Server
- Demo resiliencia
- Tests invariantes
- HTTP resiliente

---

## Benjamin Villaseñor Casian

- Cliente SSE
- Reconexión SSE
- EventRouter
- Documentación
- Evidencias
- Regresión cruzada

---

# Resultado Final

Se implementó correctamente:

- Cliente resiliente
- Circuit Breaker
- JWT
- Refresh singleton
- SSE multiplexado
- Reconexión
- Mock server
- Tests automatizados
- Regresión cruzada
- Logging
- Fail Fast
- Protección concurrente

Todos los invariantes y escenarios obligatorios fueron aprobados.

---

# Estado Final del Proyecto

| Componente | Estado |
|---|---|
| Circuit Breaker | OK |
| SSE | OK |
| JWT | OK |
| Refresh Singleton | OK |
| Mock Server | OK |
| ClienteRobusto | OK |
| Tests | OK |
| Regresión Cruzada | OK |
| Logging | OK |

---

# Evidencias Generadas

- demo_resiliencia.log
- pytest invariantes PASS
- pytest regresión PASS
- logs HTTP
- logs SSE
- logs reconexión
- screenshots terminal

---