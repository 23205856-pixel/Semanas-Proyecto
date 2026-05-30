# Certificación de Invariantes — Hito 2

## Resultado de pruebas automatizadas

Comando ejecutado:

pytest test_circuit_breaker.py -v

Resultado observado:

6 passed in 3.58s

---

## INV-A1

Resultado: PASS

Prueba ejecutada:
Se verificó que CircuitBreaker no accede ni depende
del contenido del JWT. El componente funciona incluso
con tokens malformados.

Evidencia observable:
No ocurrió ningún error de decodificación JWT.

Estado:
CircuitBreaker desacoplado del TokenManager.

---

## INV-A2

Resultado: PASS

Prueba ejecutada:
3 peticiones concurrentes fueron lanzadas en estado
SEMIABIERTO.

Evidencia observable:
Solo 1 petición alcanzó el mock y las demás recibieron
CircuitOpenError inmediato.

Estado:
Una sola petición de prueba permitida en SEMIABIERTO.

---

## INV-A3

Resultado: PASS

Prueba ejecutada:
Después de abrir el circuito con 5 fallos y realizar
una recuperación exitosa, se verificó el contador.

Evidencia observable:
_fallos_consecutivos fue reiniciado correctamente.

Estado:
cb._fallos_consecutivos == 0

---

## INV-A4

Resultado: PASS

Prueba ejecutada:
Se generaron múltiples errores 401 Unauthorized.

Evidencia observable:
Los errores de cliente no incrementaron el contador
de fallos del CircuitBreaker.

Estado:
cb.estado == CERRADO
cb._fallos_consecutivos == 0

---

## INV-B1

Resultado: PASS

Prueba ejecutada:
Se inspeccionaron los atributos internos de
TokenManager utilizando hasattr() y dir().

Evidencia observable:
No existen atributos relacionados con estados del
CircuitBreaker.

Estado:
TokenManager desacoplado del breaker.

---

## INV-B2

Resultado: PASS

Prueba ejecutada:
Se forzó un error y se inspeccionó el contenido
de los logs generados.

Evidencia observable:
El token Bearer nunca apareció en stdout/stderr,
ni completo ni truncado.

Estado:
Sin filtración de credenciales en logs.

---

## INV-B3

Resultado: PASS

Prueba ejecutada:
5 peticiones concurrentes con token expirado fueron
ejecutadas simultáneamente.

Evidencia observable:
Solo una operación refresh fue ejecutada gracias
al uso de asyncio.Lock() y double-check pattern.

Estado:
1 refresh observado para 5 peticiones concurrentes.