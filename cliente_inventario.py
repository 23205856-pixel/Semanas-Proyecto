import asyncio
import aiohttp
from datetime import datetime


BASE_URL = "http://ecomarket.local/api/v1"
TOKEN = "TOKEN_AQUI"

INTERVALO_BASE = 5
INTERVALO_MAX = 60
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
            try:
                obs.actualizar(inventario)
            except Exception as e:
                print("Error en observador:", e)


    async def _consultar_inventario(self):

        url = f"{BASE_URL}/inventario"

        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/json"
        }

        if self._ultimo_etag:
            headers["If-None-Match"] = self._ultimo_etag

        try:

            timeout = aiohttp.ClientTimeout(total=TIMEOUT)

            async with aiohttp.ClientSession(timeout=timeout) as session:

                async with session.get(url, headers=headers) as response:

                    if response.status == 200:

                        data = await response.json()

                        self._ultimo_etag = response.headers.get("ETag")

                        print("Inventario actualizado")

                        self._intervalo = INTERVALO_BASE

                        return data


                    elif response.status == 304:

                        print("Sin cambios en inventario")

                        return None


                    elif response.status == 503:

                        print("Servidor no disponible (503). Aplicando backoff...")

                        self._intervalo = min(self._intervalo * 2, INTERVALO_MAX)

                        return None


                    elif response.status in [400, 401]:

                        print("Error de cliente:", response.status)

                        return None


                    else:

                        print("Respuesta inesperada:", response.status)

                        return None


        except asyncio.TimeoutError:
            print("Timeout al consultar inventario")


        except aiohttp.ClientConnectionError:

            print("Error de conexión con el servidor - usando datos simulados")

            return {
                "productos":[
                    {
                        "id":"PROD-001",
                        "nombre":"Arroz Premium",
                        "stock_actual":45,
                        "stock_minimo":50,
                        "status":"BAJO_MINIMO"
                    },
                    {
                        "id":"PROD-002",
                        "nombre":"Frijol",
                        "stock_actual":100,
                        "stock_minimo":50,
                        "status":"OK"
                    }
                ]
            }


        except Exception as e:
            print("Error inesperado:", e)

        return None


    async def iniciar(self):

        self._ejecutando = True

        while self._ejecutando:

            datos = await self._consultar_inventario()

            if datos:
                self._notificar(datos)

            await asyncio.sleep(self._intervalo)


    def detener(self):
        self._ejecutando = False


# ==========================
# MODULO COMPRAS
# ==========================

class ModuloCompras(Observador):

    def actualizar(self, inventario):

        productos = inventario.get("productos", [])

        for p in productos:

            if p.get("status") == "BAJO_MINIMO":

                print("\n⚠ Producto bajo mínimo")

                print("ID:", p.get("id"))
                print("Nombre:", p.get("nombre"))
                print("Stock:", p.get("stock_actual"))
                print("Stock mínimo:", p.get("stock_minimo"))


# ==========================
# MODULO ALERTAS
# ==========================

class ModuloAlertas(Observador):

    def actualizar(self, inventario):

        productos = inventario.get("productos", [])

        for p in productos:

            if p.get("status") == "BAJO_MINIMO":

                alerta = {
                    "producto_id": p.get("id"),
                    "stock_actual": p.get("stock_actual"),
                    "stock_minimo": p.get("stock_minimo"),
                    "timestamp": datetime.utcnow().isoformat()
                }

                print("\n🚨 Enviando alerta:", alerta)


# ==========================
# PROGRAMA PRINCIPAL
# ==========================

async def main():

    monitor = MonitorInventario()

    compras = ModuloCompras()
    alertas = ModuloAlertas()

    monitor.suscribir(compras)
    monitor.suscribir(alertas)

    await monitor.iniciar()


if __name__ == "__main__":

    asyncio.run(main())