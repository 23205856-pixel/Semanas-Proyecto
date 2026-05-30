import asyncio
import aiohttp

from circuit_breaker import (
    CircuitBreaker,
    CircuitOpenError,
    ServerFailureError,
    ClientFailureError,
    EstadoCircuito
)

from token_manager import TokenManager


class ClienteRobusto:

    def __init__(
        self,
        base_url: str,
        token_manager: TokenManager,
        circuit_breaker: CircuitBreaker
    ):

        self._base_url = base_url

        self._tm = token_manager
        self._cb = circuit_breaker

        self._observers = []

    def agregar_observer(self, callback):

        self._observers.append(callback)

    def _notificar_ui(self, mensaje):

        for callback in self._observers:
            callback(mensaje)

    async def _hacer_request(
        self,
        method: str,
        ruta: str
    ):

        token = self._tm.get_auth_header()

        timeout = aiohttp.ClientTimeout(
            total=5
        )

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.request(
                method,
                f"{self._base_url}{ruta}",
                headers=token
            ) as response:

                if response.status == 401:

                    refreshed = (
                        await self._tm
                        .refresh_access_token()
                    )

                    if not refreshed:

                        self._tm.logout()

                        raise ClientFailureError(
                            "Sesión expirada"
                        )

                    return await self._hacer_request(
                        method,
                        ruta
                    )

                if 500 <= response.status < 600:

                    raise ServerFailureError(
                        f"HTTP {response.status}"
                    )

                if 400 <= response.status < 500:

                    raise ClientFailureError(
                        f"HTTP {response.status}"
                    )

                return await response.json()

    async def get(self, ruta: str):

        estado_anterior = self._cb.estado

        try:

            resultado = await self._cb.ejecutar(
                self._hacer_request,
                "GET",
                ruta
            )

            if (
                estado_anterior
                != EstadoCircuito.CERRADO
                and self._cb.estado
                == EstadoCircuito.CERRADO
            ):

                self._notificar_ui(
                    "Conexión restaurada"
                )

            return resultado

        except CircuitOpenError:

            self._notificar_ui(
                "Servidor temporalmente no disponible"
            )

            raise

        except Exception:

            if (
                estado_anterior
                != EstadoCircuito.ABIERTO
                and self._cb.estado
                == EstadoCircuito.ABIERTO
            ):

                self._notificar_ui(
                    "Circuito ABIERTO"
                )

            raise