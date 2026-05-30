import asyncio
import logging
import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from aiohttp import web

from mock.mock_server import ServidorMockEcoMarket

from cliente_robusto import ClienteRobusto

from circuit_breaker import (
    CircuitBreaker,
    CircuitOpenError,
    EstadoCircuito
)

from token_manager import TokenManager


# =========================================================
# LOGGING → demo_resiliencia.log
# =========================================================

logging.basicConfig(
    filename="demo_resiliencia.log",
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    filemode="w"
)

logger = logging.getLogger(__name__)

def ui_callback(mensaje):

    print(f"[UI] {mensaje}")

    logger.info(f"[UI] {mensaje}")

async def demo():


    mock = ServidorMockEcoMarket()

    runner = web.AppRunner(mock.app)

    await runner.setup()

    site = web.TCPSite(
        runner,
        "localhost",
        9000
    )

    await site.start()

    print("[MOCK] Servidor activo en http://localhost:9000")

    logger.info(
        "[MOCK] Servidor activo en http://localhost:9000"
    )


    tm = TokenManager()

    cb = CircuitBreaker(
        umbral_fallos=5,
        timeout_apertura=5
    )

    cliente = ClienteRobusto(
        "http://localhost:9000",
        tm,
        cb
    )

    cliente.agregar_observer(
        ui_callback
    )

    print("\n=== ESCENARIO 1: RESPUESTAS 200 ===")

    logger.info("=== ESCENARIO 1 ===")

    mock.modo = "normal"

    for i in range(3):

        try:

            data = await cliente.get(
                "/api/inventario"
            )

            msg = (
                f"[HTTP #{i+1}] 200 "
                f"| productos={data['productos']} "
                f"| CB={cb.estado.name} "
                f"| fallos={cb._fallos_consecutivos}"
            )

            print(msg)

            logger.info(msg)

        except Exception as e:

            print(e)

            logger.error(str(e))

    print("\n=== ESCENARIO 2: FALLAS 503 ===")

    logger.info("=== ESCENARIO 2 ===")

    mock.modo = "fallo_503"

    for i in range(6):

        try:

            await cliente.get(
                "/api/inventario"
            )

        except CircuitOpenError as e:

            msg = (
                f"[BREAKER] OPEN "
                f"| fail fast "
                f"| restante={e.tiempo_restante:.1f}s"
            )

            print(msg)

            logger.warning(msg)

        except Exception as e:

            msg = (
                f"[HTTP ERROR] {e} "
                f"| CB={cb.estado.name} "
                f"| fallos={cb._fallos_consecutivos}"
            )

            print(msg)

            logger.warning(msg)

    print("\nEsperando transición a SEMIABIERTO...\n")

    logger.info(
        "Esperando transición a SEMIABIERTO"
    )

    await asyncio.sleep(6)

    print(
        f"[CB] Estado actual: {cb.estado.name}"
    )

    logger.info(
        f"[CB] Estado actual: {cb.estado.name}"
    )

    print("\n=== ESCENARIO 3: RECUPERACION ===")

    logger.info("=== ESCENARIO 3 ===")

    mock.modo = "normal"

    try:

        data = await cliente.get(
            "/api/inventario"
        )

        msg = (
            f"[RECOVERY] 200 "
            f"| productos={data['productos']} "
            f"| CB={cb.estado.name} "
            f"| fallos={cb._fallos_consecutivos}"
        )

        print(msg)

        logger.info(msg)

    except Exception as e:

        print(e)

        logger.error(str(e))

    final = (
        f"\nEstado final → "
        f"CB={cb.estado.name} "
        f"| fallos={cb._fallos_consecutivos}"
    )

    print(final)

    logger.info(final)

    await runner.cleanup()

if __name__ == "__main__":

    asyncio.run(demo())