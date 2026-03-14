import asyncio
import aiohttp


BASE_URL = "http://ecomarket.local/api/v1"
TOKEN = "TOKEN_AQUI"

INTERVALO_BASE = 5


class Observador:
    def actualizar(self, inventario):
        pass


class MonitorInventario:

    def __init__(self):
        self._observadores = []
        self._ejecutando = False
        self._intervalo = INTERVALO_BASE


    def suscribir(self, obs):
        self._observadores.append(obs)


    def desuscribir(self, obs):
        self._observadores.remove(obs)


    def _notificar(self, inventario):

        for obs in self._observadores:
            obs.actualizar(inventario)


    async def _consultar_inventario(self):

        url = f"{BASE_URL}/inventario"

        headers = {
            "Authorization": f"Bearer {TOKEN}"
        }

        async with aiohttp.ClientSession() as session:

            async with session.get(url, headers=headers) as response:

                data = await response.json()

                return data


    async def iniciar(self):

        self._ejecutando = True

        while self._ejecutando:

            datos = await self._consultar_inventario()

            if datos:
                self._notificar(datos)

            await asyncio.sleep(self._intervalo)


class ModuloCompras(Observador):

    def actualizar(self, inventario):
        print("Actualización recibida")


async def main():

    monitor = MonitorInventario()

    compras = ModuloCompras()

    monitor.suscribir(compras)

    await monitor.iniciar()


if __name__ == "__main__":
    asyncio.run(main())