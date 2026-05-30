import asyncio
import time
from enum import Enum, auto


class ServerFailureError(Exception):
    """Fallo real del backend."""


class ClientFailureError(Exception):
    """Fallo del cliente — NO debe abrir el breaker."""


class CircuitOpenError(Exception):
    """El circuito está abierto y no permite tráfico."""

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


class CircuitBreaker:

    def __init__(
        self,
        umbral_fallos: int = 5,
        timeout_apertura: float = 60.0,
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

    def _revisar_timeout(self):

        if self._estado == EstadoCircuito.ABIERTO:

            tiempo_transcurrido = (
                time.monotonic() - self._tiempo_apertura
            )

            if tiempo_transcurrido >= self._timeout_apertura:

                self._estado = EstadoCircuito.SEMIABIERTO

    def _registrar_exito(self):

        self._fallos_consecutivos = 0
        self._tiempo_apertura = None

        self._estado = EstadoCircuito.CERRADO

    def _registrar_fallo(self):

        self._fallos_consecutivos += 1

        if (
            self._fallos_consecutivos
            >= self._umbral_fallos
        ):

            self._estado = EstadoCircuito.ABIERTO

            self._tiempo_apertura = time.monotonic()

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