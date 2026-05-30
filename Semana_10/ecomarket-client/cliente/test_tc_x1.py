import asyncio
import io

from circuit_breaker import (
    CircuitBreaker,
    ServerFailureError
)

from cliente_sse_multiplex import (
    ClienteSSEMultiplex,
    MODULOS_ACTIVOS
)


async def main():

    print("\n=== TC-X1 ===")
    print("SSE activo mientras CB transiciona a ABIERTO\n")

    cliente_sse = ClienteSSEMultiplex(
        MODULOS_ACTIVOS
    )

    eventos_recibidos = []

    def handler_precio(datos):

        eventos_recibidos.append(datos)

        print(
            f"[SSE] Evento recibido: {datos}"
        )

    cliente_sse.suscribir(
        "precio-actualizado",
        handler_precio
    )

    stream = io.StringIO(
        "id: evt-500\n"
        "event: precio-actualizado\n"
        "data: {\"producto_id\":\"P1\",\"precio_nuevo\":99}\n\n"
    )

    cb = CircuitBreaker(
        umbral_fallos=5,
        timeout_apertura=5
    )

    async def fallo():
        raise ServerFailureError("503")

    for i in range(5):

        try:
            await cb.ejecutar(fallo)

        except Exception:
            pass

    print(
        f"[CB] Estado actual: {cb.estado.name}"
    )

    cliente_sse._leer_stream(stream)

    print(
        f"[SSE] Eventos procesados: "
        f"{len(eventos_recibidos)}"
    )

    print("\n=== RESULTADO ===")

    if (
        cb.estado.name == "ABIERTO"
        and len(eventos_recibidos) == 1
    ):

        print(
            "OK → El SSE continuó funcionando "
            "mientras el Circuit Breaker HTTP "
            "estaba ABIERTO."
        )

    else:

        print("FAIL")


if __name__ == "__main__":
    asyncio.run(main())