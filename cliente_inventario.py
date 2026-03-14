import asyncio
import aiohttp


BASE_URL = "http://ecomarket.local/api/v1"
TOKEN = "TOKEN_AQUI"

INTERVALO_BASE = 5
TIMEOUT = 10


class Observador:
    def actualizar(self, inventario):
        pass


class MonitorInventario:

    def __init__(self):
        self._observadores = []
        self._ultimo_etag = None
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
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/json"
        }

        if self._ultimo_etag:
            headers["If-None-Match"] = self._ultimo_etag

        timeout = aiohttp.ClientTimeout(total=TIMEOUT)

        async with aiohttp.ClientSession(timeout=timeout) as session:

            async with session.get(url, headers=headers) as response:

                if response.status == 200:

                    data = await response.json()

                    self._ultimo_etag = response.headers.get("ETag")

                    print("Inventario actualizado")

                    return data


                elif response.status == 304:

                    print("Sin cambios en inventario")

                    return None


                else:

                    print("Error:", response.status)

                    return None


    async def iniciar(self):

        self._ejecutando = True

        while self._ejecutando:

            datos = await self._consultar_inventario()

            if datos:
                self._notificar(datos)

            await asyncio.sleep(self._intervalo)


class ModuloCompras(Observador):

    def actualizar(self, inventario):

        productos = inventario.get("productos", [])

        for p in productos:

            if p.get("status") == "BAJO_MINIMO":
                print("Producto bajo mínimo:", p.get("nombre"))


async def main():

    monitor = MonitorInventario()

    compras = ModuloCompras()

    monitor.suscribir(compras)

    await monitor.iniciar()


if __name__ == "__main__":
    asyncio.run(main())