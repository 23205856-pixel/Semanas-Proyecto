from cliente_sse_multiplex import (
    ClienteSSEMultiplex,
    MODULOS_ACTIVOS
)


def main():

    print("\n=== TC-X3 ===")

    cliente = ClienteSSEMultiplex(
        MODULOS_ACTIVOS
    )

    cliente.ultimo_id = "evt-900"

    headers = cliente._reconectar()

    print(
        f"Headers reconexión: {headers}"
    )

    print(
        f"Last Event ID guardado: "
        f"{cliente.ultimo_id}"
    )

    print("\n=== RESULTADO ===")

    if (
        headers.get("Last-Event-ID")
        == "evt-900"
    ):

        print(
            "OK → Reconexión SSE conserva "
            "Last-Event-ID correctamente."
        )

    else:

        print("FAIL")


if __name__ == "__main__":
    main()