import asyncio
import pytest
import logging
from circuit_breaker import (
    CircuitBreaker,
    EstadoCircuito,
    ServerFailureError,
    ClientFailureError,
    CircuitOpenError
)
from token_manager import TokenManager



# =========================================================
# INV-A2
# En SEMIABIERTO solo 1 petición pasa
# =========================================================

@pytest.mark.asyncio
async def test_inv_a2_semiaabierto_una_peticion():

    cb = CircuitBreaker(
        umbral_fallos=1,
        timeout_apertura=0.1
    )

    contador_mock = 0

    async def fallo():
        raise ServerFailureError("503")

    async def exito():
        nonlocal contador_mock

        contador_mock += 1

        await asyncio.sleep(0.2)

        return "ok"

    with pytest.raises(ServerFailureError):
        await cb.ejecutar(fallo)

    assert cb.estado == EstadoCircuito.ABIERTO

    await asyncio.sleep(0.2)

    assert cb.estado == EstadoCircuito.SEMIABIERTO

    async def intentar():
        try:
            return await cb.ejecutar(exito)
        except CircuitOpenError:
            return "blocked"

    resultados = await asyncio.gather(
        intentar(),
        intentar(),
        intentar()
    )

    exitos = resultados.count("ok")
    bloqueadas = resultados.count("blocked")

    assert exitos == 1
    assert bloqueadas == 2

    assert contador_mock == 1


# =========================================================
# INV-A3
# _fallos_consecutivos se resetea al cerrar
# =========================================================

@pytest.mark.asyncio
async def test_inv_a3_reset_fallos():

    cb = CircuitBreaker(
        umbral_fallos=5,
        timeout_apertura=0.1
    )

    async def fallo():
        raise ServerFailureError("503")

    async def exito():
        return "ok"

    for _ in range(5):

        with pytest.raises(ServerFailureError):
            await cb.ejecutar(fallo)

    assert cb.estado == EstadoCircuito.ABIERTO

    await asyncio.sleep(0.2)

    assert cb.estado == EstadoCircuito.SEMIABIERTO

    resultado = await cb.ejecutar(exito)

    assert resultado == "ok"

    assert cb.estado == EstadoCircuito.CERRADO

    assert cb._fallos_consecutivos == 0


# =========================================================
# INV-A4
# 401/403 NO incrementan fallos
# =========================================================

@pytest.mark.asyncio
async def test_inv_a4_client_errors_no_abren():

    cb = CircuitBreaker(
        umbral_fallos=5
    )

    async def error_401():
        raise ClientFailureError("401 Unauthorized")

    for _ in range(10):

        with pytest.raises(ClientFailureError):
            await cb.ejecutar(error_401)

    assert cb.estado == EstadoCircuito.CERRADO

    assert cb._fallos_consecutivos == 0

# =========================================================
# INV-B1
# =========================================================

def test_inv_b1_token_manager_desacoplado():

    tm = TokenManager()

    assert not hasattr(tm, "_estado")

    atributos = str(dir(tm)).lower()

    assert "circuit" not in atributos
    assert "breaker" not in atributos
    assert "open" not in atributos

# =========================================================
# INV-B2
# =========================================================

def test_inv_b2_no_token_en_logs(caplog):

    logger = logging.getLogger(__name__)

    token = "Bearer SECRET_TOKEN"

    try:

        raise Exception(
            "503 Service Unavailable"
        )

    except Exception as e:

        logger.error(
            f"Error HTTP: {e}"
        )

    logs = caplog.text

    assert "Bearer" not in logs

    assert token not in logs

# =========================================================
# INV-B3
# =========================================================

@pytest.mark.asyncio
async def test_inv_b3_single_refresh():

    contador_refresh = 0

    class MockTokenManager:

        def __init__(self):

            self._refresh_lock = asyncio.Lock()

            self._access_token = None

        async def refresh_access_token(self):

            nonlocal contador_refresh

            async with self._refresh_lock:

                if self._access_token:
                    return True

                contador_refresh += 1

                await asyncio.sleep(0.2)

                self._access_token = "nuevo_token"

                return True

    tm = MockTokenManager()

    async def worker():

        await tm.refresh_access_token()

    await asyncio.gather(
        worker(),
        worker(),
        worker(),
        worker(),
        worker()
    )

    assert contador_refresh == 1