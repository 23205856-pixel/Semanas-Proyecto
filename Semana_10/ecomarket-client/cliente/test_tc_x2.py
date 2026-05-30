import asyncio
import pytest

from circuit_breaker import (
    CircuitBreaker,
    EstadoCircuito,
    ServerFailureError
)


class MockTokenManager:

    def __init__(self):

        self.refresh_count = 0

    def is_expiring_soon(self):

        return True

    async def refresh_access_token(self):

        self.refresh_count += 1

        await asyncio.sleep(0.1)

        return True


@pytest.mark.asyncio
async def test_tc_x2_refresh_semiaabierto():

    cb = CircuitBreaker(
        umbral_fallos=1,
        timeout_apertura=0.1
    )

    tm = MockTokenManager()

    peticiones_mock = 0

    async def fallo():
        raise ServerFailureError("503")

    async def exito():

        nonlocal peticiones_mock

        peticiones_mock += 1

        return "ok"

    # ======================================
    # Abrir circuito
    # ======================================

    with pytest.raises(ServerFailureError):
        await cb.ejecutar(fallo)

    assert cb.estado == EstadoCircuito.ABIERTO

    # Esperar transición
    await asyncio.sleep(0.2)

    assert cb.estado == EstadoCircuito.SEMIABIERTO

    # ======================================
    # REFRESH PRIMERO
    # ======================================

    if tm.is_expiring_soon():

        await tm.refresh_access_token()

    resultado = await cb.ejecutar(exito)

    # ======================================
    # Verificaciones
    # ======================================

    assert resultado == "ok"

    assert tm.refresh_count == 1

    assert peticiones_mock == 1

    assert cb.estado == EstadoCircuito.CERRADO