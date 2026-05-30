import asyncio
import aiohttp
import base64
import json
import time

from enum import Enum, auto
from typing import Optional

class ServerFailureError(Exception):
    """Fallo real del backend."""


class ClientFailureError(Exception):
    """Fallo del cliente."""


class CircuitOpenError(Exception):
    """El circuito está abierto."""

    def __init__(self, tiempo_restante: float):

        self.tiempo_restante = tiempo_restante

        super().__init__(
            f"Circuit breaker abierto. "
            f"Reintenta en {tiempo_restante:.1f}s"
        )


class EstadoCircuito(Enum):
    CERRADO = auto()
    ABIERTO = auto()
    SEMIABIERTO = auto()

ui_state = {
    "banner": None,
    "checkout_enabled": True
}


def on_circuit_open():

    ui_state["banner"] = (
        "Servidor temporalmente no disponible"
    )

    ui_state["checkout_enabled"] = False

    print(
        "[UI] banner=Servidor temporalmente no disponible "
        "· action=disable_checkout"
    )


def on_circuit_closed():

    ui_state["banner"] = None

    ui_state["checkout_enabled"] = True

    print(
        "[UI] banner=oculto · action=enable_checkout"
    )

class CircuitBreaker:

    def __init__(
        self,
        umbral_fallos: int = 5,
        timeout_apertura: float = 5.0,
        nombre: str = "EcoMarketAPI"
    ):

        self._umbral_fallos = umbral_fallos
        self._timeout_apertura = timeout_apertura
        self._nombre = nombre

        self._estado = EstadoCircuito.CERRADO

        self._fallos_consecutivos = 0
        self._tiempo_apertura = None

        self._lock = asyncio.Lock()

        self._peticion_prueba_en_curso = False

    @property
    def estado(self):

        self._revisar_timeout()
        return self._estado

    @property
    def fallos(self):
        return self._fallos_consecutivos

    def _revisar_timeout(self):

        if self._estado == EstadoCircuito.ABIERTO:

            tiempo_transcurrido = (
                time.monotonic() - self._tiempo_apertura
            )

            if tiempo_transcurrido >= self._timeout_apertura:

                self._estado = EstadoCircuito.SEMIABIERTO

                print(
                    f"[BREAKER] Timeout "
                    f"{self._timeout_apertura:.0f}s "
                    f"→ SEMIABIERTO"
                )

    def _registrar_exito(self):

        estado_anterior = self._estado

        self._fallos_consecutivos = 0
        self._tiempo_apertura = None

        self._estado = EstadoCircuito.CERRADO

        if estado_anterior != EstadoCircuito.CERRADO:
            on_circuit_closed()

    def _registrar_fallo(self):

        self._fallos_consecutivos += 1

        if (
            self._fallos_consecutivos
            >= self._umbral_fallos
        ):

            self._estado = EstadoCircuito.ABIERTO

            self._tiempo_apertura = time.monotonic()

            on_circuit_open()

    def _es_fallo_servidor(
        self,
        exception: Exception
    ) -> bool:

        return isinstance(
            exception,
            ServerFailureError
        )

    async def ejecutar(self, fn, *args, **kwargs):

        estado_actual = self.estado

        if estado_actual == EstadoCircuito.ABIERTO:

            tiempo_restante = (
                self._timeout_apertura
                - (
                    time.monotonic()
                    - self._tiempo_apertura
                )
            )

            raise CircuitOpenError(
                max(tiempo_restante, 0)
            )

        lock_semiaabierto = False

        if estado_actual == EstadoCircuito.SEMIABIERTO:

            async with self._lock:

                if self._peticion_prueba_en_curso:

                    raise CircuitOpenError(
                        self._timeout_apertura
                    )

                self._peticion_prueba_en_curso = True
                lock_semiaabierto = True

        try:

            resultado = await fn(*args, **kwargs)

            self._registrar_exito()

            return resultado

        except Exception as e:

            if self._es_fallo_servidor(e):
                self._registrar_fallo()

            raise

        finally:

            if lock_semiaabierto:

                async with self._lock:
                    self._peticion_prueba_en_curso = False

class TokenManager:

    def __init__(self):

        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None

    def decode_payload(self, token: str):

        _, payload, _ = token.split('.')

        payload += '=' * (-len(payload) % 4)

        decoded = base64.b64decode(payload)

        return json.loads(decoded)

    async def login(self):

        async with aiohttp.ClientSession() as session:

            async with session.post(
                "http://localhost:8888/auth/login"
            ) as resp:

                data = await resp.json()

                self._access_token = (
                    data["access_token"]
                )

                self._refresh_token = (
                    data["refresh_token"]
                )

                payload = self.decode_payload(
                    self._access_token
                )

                print(
                    f"[LOGIN] Token almacenado "
                    f"· rol={payload['rol']}"
                )

    def get_auth_header(self):

        return {
            "Authorization": (
                f"Bearer {self._access_token}"
            )
        }

    def token_valido(self):
        return self._access_token is not None

class ClienteRobusto:

    def __init__(self, tm, cb):

        self._tm = tm
        self._cb = cb

        self._contador_http = 0

    async def get_inventario(self):

        self._contador_http += 1

        headers = self._tm.get_auth_header()

        async def request():

            async with aiohttp.ClientSession() as session:

                async with session.get(
                    "http://localhost:8888/api/inventario",
                    headers=headers
                ) as resp:

                    if resp.status >= 500:

                        raise ServerFailureError(
                            f"{resp.status} Service Unavailable"
                        )

                    if resp.status >= 400:

                        raise ClientFailureError(
                            f"{resp.status} Client Error"
                        )

                    return await resp.json()

        try:

            data = await self._cb.ejecutar(request)

            print(
                f"[HTTP #{self._contador_http}] "
                f"200 · productos={data['productos']} "
                f"· CB: {self._cb.estado.name} "
                f"(fallos={self._cb.fallos})"
            )

            return data

        except ServerFailureError as e:

            if self._cb.estado == EstadoCircuito.ABIERTO:

                print(
                    f"[HTTP #{self._contador_http}] "
                    f"503 · CB: ABIERTO "
                    f"(umbral alcanzado)"
                )

            else:

                print(
                    f"[HTTP #{self._contador_http}] "
                    f"503 · CB: {self._cb.estado.name} "
                    f"(fallos={self._cb.fallos})"
                )

            raise

async def main():

    tm = TokenManager()

    cb = CircuitBreaker(
        umbral_fallos=5,
        timeout_apertura=5
    )

    cliente = ClienteRobusto(tm, cb)

    await tm.login()

    for _ in range(10):

        try:

            await cliente.get_inventario()

        except CircuitOpenError:

            print(
                "[BREAKER] Fail fast — "
                "CircuitOpenError "
                "(sin tocar el servidor)"
            )

            await asyncio.sleep(6)

        except ServerFailureError:
            pass

        await asyncio.sleep(0.5)

    print(
        f"Estado final: "
        f"circuito={cb.estado.name} "
        f"· token_válido={tm.token_valido()}"
    )


if __name__ == "__main__":
    asyncio.run(main())