"""
====RETO IA 3 (REFLEXIONA)==== 
DECISIONES DE DISEÑO — ClienteSSEMultiplex para EcoMarket
==========================================================

MODULOS_ACTIVOS = ["precios", "inventario", "pedidos"]
→ Elegí estos módulos porque son los más críticos para la operación en tiempo real. El trade-off es que al incluir más módulos, aumenta el volumen de eventos que el cliente debe procesar, pero evito abrir múltiples conexiones.

TIMEOUT = 30
→ Elegí 30 segundos porque permite tolerar latencias altas (como redes corporativas). Un timeout menor podría causar reconexiones innecesarias si la conexión tarda en establecerse.

MAX_REINTENTOS = 5
→ Elegí 5 reintentos para permitir recuperación ante fallos breves. El trade-off es que si el servidor tarda mucho en volver (por ejemplo horas), el cliente se rendirá rápido y dejará de intentar reconectarse.

Trade-off principal (una conexión vs. múltiples):
→ Usar una sola conexión multiplexada simplifica el código y reduce la gestión de múltiples conexiones. Sin embargo, si la conexión se pierde, se dejan de recibir eventos de todos los módulos al mismo tiempo.

Limitación pendiente:
→ El cliente no maneja reconexión automática prolongada ni persistencia de estado. Además, al reconectar para agregar módulos, puede perder eventos durante ese intervalo.

# Resumen de la IA validado sin correcciones.
"""

import json
import io

BASE_URL = "http://localhost:3000"

TIMEOUT = 30
MAX_REINTENTOS = 5
ESPERA_INICIAL = 1
MODULOS_ACTIVOS = ["precios", "inventario", "pedidos"]


# ROUTER
class EventRouter:
    def __init__(self):
        self.handlers = {}

    def registrar(self, tipo, fn):
        if tipo not in self.handlers:
            self.handlers[tipo] = []
        self.handlers[tipo].append(fn)

    def despachar(self, tipo, datos):
        if tipo not in self.handlers:
            print(f"[WARN] Evento desconocido ignorado: {tipo}")
            return

        for fn in self.handlers[tipo]:
            try:
                fn(datos)
            except Exception as e:
                print(f"[ERROR] Handler '{tipo}' falló: {e}")


# CLIENTE
class ClienteSSEMultiplex:

    def __init__(self, modulos):
        self.modulos = modulos
        self.router = EventRouter()
        self.estado = "DESCONECTADO"
        self.ultimo_id = None

    def suscribir(self, tipo_evento, handler_fn):
        self.router.registrar(tipo_evento, handler_fn)

    def construir_url(self):
        if not self.modulos:
            raise ValueError("Debe haber al menos un módulo")
        return BASE_URL + "?modulos=" + ",".join(self.modulos)

    def _parsear_linea(self, linea, evento_parcial):
        if linea.startswith(":"):
            return evento_parcial

        if ":" in linea:
            campo, valor = linea.split(":", 1)
            valor = valor.strip()
        else:
            campo = linea
            valor = ""

        evento_parcial[campo] = valor
        return evento_parcial

    def _procesar_evento(self, evento_parcial):
        if not evento_parcial:
            return {}

        if "id" in evento_parcial:
            self.ultimo_id = evento_parcial["id"]

        tipo = evento_parcial.get("event", "message")
        data = evento_parcial.get("data", "{}")

        try:
            datos = json.loads(data)
        except Exception:
            print(f"[ERROR] JSON inválido en evento '{tipo}': {data}")
            datos = {}

        self.router.despachar(tipo, datos)

        return {}

    def _leer_stream(self, stream):
        evento_parcial = {}

        for linea in stream:
            linea = linea.strip()

            if linea == "":
                evento_parcial = self._procesar_evento(evento_parcial)
            else:
                evento_parcial = self._parsear_linea(linea, evento_parcial)

    def _reconectar(self):
        print(f"[RECONEXION] Reintentando con Last-Event-ID: {self.ultimo_id}")

        headers = {}
        if self.ultimo_id:
            headers["Last-Event-ID"] = self.ultimo_id

        return headers

    def iniciar(self):
        if self.estado != "DESCONECTADO":
            print("Ya conectado")
            return

        self.estado = "CONECTADO"

        stream = io.StringIO(generar_stream_mock())
        self._leer_stream(stream)


# HANDLERS
def handler_precio_actualizado(datos):
    if datos.get("producto_id") == "FORZAR_EXCEPCION":
        raise Exception("Error simulado")

    anterior = datos.get("precio_anterior", 0)
    nuevo = datos.get("precio_nuevo", 0)

    if anterior == 0:
        return

    cambio = (nuevo - anterior) / anterior

    if cambio > 0.05:
        print(f"[ALERTA] Cambio mayor al 5%: {datos}")


def handler_stock_critico(datos):
    stock = datos.get("stock_actual", 0)

    if stock <= 3:
        print(f"[CRITICO] Stock muy bajo: {datos}")
    elif stock <= 10:
        print(f"[BAJO] Stock bajo: {datos}")


pedidos = []


def handler_pedido_nuevo(datos):
    if datos.get("total", 0) > 500:
        pedidos.append(datos)
        print(f"[PEDIDO] Registrado: {datos}")


def handler_heartbeat(datos):
    print(f"[PING] Activo: {datos.get('timestamp')}")


# MOCKS DE TEST
def generar_stream_mock():
    return (
        "id: evt-001\nevent: precio-actualizado\n"
        "data: {\"producto_id\": \"P042\", \"precio_anterior\": 89.0, \"precio_nuevo\": 79.5}\n\n"

        "id: evt-002\nevent: stock-critico\n"
        "data: {\"producto_id\": \"P019\", \"stock_actual\": 3}\n\n"
    )


def stream_malformado():
    return (
        "id: evt-100\n"
        "event: precio-actualizado\n"
        "data: ERROR_INTERNO_SERVIDOR_PARSE_FAILED\n\n"

        "id: evt-101\n"
        "event: sistema-ping\n"
        "data: {\"timestamp\": \"ok\"}\n\n"
    )


def stream_evento_desconocido():
    return (
        "id: evt-200\n"
        "event: alerta-fraude\n"
        "data: {\"riesgo\": \"alto\"}\n\n"
    )


# TESTS DE VALIDACION
def ejecutar_tests():
    print("\n===== VALIDACION CLIENTE SSE =====\n")

    cliente = ClienteSSEMultiplex(MODULOS_ACTIVOS)

    cliente.suscribir("precio-actualizado", handler_precio_actualizado)
    cliente.suscribir("stock-critico", handler_stock_critico)
    cliente.suscribir("pedido-nuevo", handler_pedido_nuevo)
    cliente.suscribir("sistema-ping", handler_heartbeat)

    # ESCENARIO 1
    print("\n[ESCENARIO 1] JSON malformado")
    stream = io.StringIO(stream_malformado())
    cliente._leer_stream(stream)
    print("Resultado: OK si no crashea\n")

    # ESCENARIO 2
    print("[ESCENARIO 2] Reconexión con Last-Event-ID")
    cliente.ultimo_id = "5"
    headers = cliente._reconectar()
    print("Headers:", headers)
    print("Resultado:", "OK" if headers.get("Last-Event-ID") == "5" else "FAIL", "\n")

    # ESCENARIO 3
    print("[ESCENARIO 3] Evento desconocido")
    stream = io.StringIO(stream_evento_desconocido())
    cliente._leer_stream(stream)
    print("Resultado: OK si no hay excepción\n")

    # ESCENARIO 4
    print("[ESCENARIO 4] iniciar() doble")
    cliente.estado = "DESCONECTADO"
    cliente.iniciar()
    cliente.iniciar()
    print("Resultado: OK si evita doble conexión\n")

    print("===== FIN VALIDACION =====\n")


# MAIN
if __name__ == "__main__":
    cliente = ClienteSSEMultiplex(MODULOS_ACTIVOS)

    cliente.suscribir("precio-actualizado", handler_precio_actualizado)
    cliente.suscribir("stock-critico", handler_stock_critico)
    cliente.suscribir("pedido-nuevo", handler_pedido_nuevo)
    cliente.suscribir("sistema-ping", handler_heartbeat)

    cliente.iniciar()

    ejecutar_tests()