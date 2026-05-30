# Bug A — Violación de autorización en GET de inventario

## Síntoma
Los operadores con rol `viewer` reciben un error de permisos al consultar inventario, aunque deberían poder realizar operaciones GET.

## Causa raíz
El método `CircuitBreaker.ejecutar()` está decodificando el JWT y validando roles directamente dentro del Circuit Breaker.  
Esto introduce lógica de autorización en un componente cuya responsabilidad debe limitarse al control de resiliencia y tolerancia a fallos.

## Línea exacta
```python
if payload.get('rol') not in ('admin', 'supervisor'):
    raise PermissionError(f"Rol '{payload['rol']}' no autorizado")
```

## Corrección
Eliminar completamente el bloque:

```python
if token_manager:
    token = token_manager.get_access_token()
    pad = 4 - len(token.split('.')[1]) % 4
    payload = json.loads(
        base64.urlsafe_b64decode(token.split('.')[1] + '=' * pad)
    )
    if payload.get('rol') not in ('admin', 'supervisor'):
        raise PermissionError(f"Rol '{payload['rol']}' no autorizado")
```

La autorización debe pertenecer a un componente especializado de autenticación/autorización y no al Circuit Breaker.

## Principio violado
- SRP (Single Responsibility Principle)
- INV-A1: El Circuit Breaker no debe depender del contenido del token ni aplicar reglas de autorización.

---

# Bug B — Exposición de token en logs

## Síntoma
En los logs de producción aparecen fragmentos del token de acceso.

## Causa raíz
El logger imprime parcialmente el encabezado `Authorization`, exponiendo información sensible del bearer token en logs de error.

## Línea exacta
```python
logger.error(
    f"Error: {e}. Auth: {headers['Authorization'][:40]}..."
)
```

## Corrección
Eliminar cualquier interpolación del token y registrar únicamente información operacional segura.

Ejemplo:

```python
logger.error(f"Error durante GET /api/inventario: {e}")
```

## Principio violado
- Seguridad de información sensible
- INV-B2: Ningún secreto o token debe aparecer en logs.

---

# Bug C — Contador de fallos no reiniciado

## Síntoma
Después de que el servidor se recupera y el circuito vuelve a estado `CERRADO`, el contador de fallos sigue acumulándose.

## Causa raíz
El método `_on_exito()` cambia el estado del circuito a `CERRADO`, pero no reinicia el contador interno `_fallos`.

## Línea exacta
```python
self.estado = EstadoCircuito.CERRADO
```

## Corrección
Agregar el reinicio explícito del contador:

```python
def _on_exito(self):
    self.estado = EstadoCircuito.CERRADO
    self._fallos = 0
```

## Principio violado
- INV-A3: Un Circuit Breaker recuperado debe reiniciar su historial de fallos.
- Consistencia de estado interno.