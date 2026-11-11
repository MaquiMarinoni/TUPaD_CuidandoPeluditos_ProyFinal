
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from http.cookiejar import CookieJar
from threading import Barrier
from urllib.error import HTTPError
from urllib.request import (
    HTTPCookieProcessor,
    Request,
    build_opener,
)
import json
import uuid


BASE = "http://127.0.0.1:5000"
PASSWORD = "PruebaLocal2026!"
ERRORES = 0


class Cliente:
    def __init__(self):
        self.opener = build_opener(
            HTTPCookieProcessor(CookieJar())
        )
        self.csrf = None

    def enviar(self, metodo, ruta, datos=None):
        cuerpo = None
        headers = {}

        if datos is not None:
            cuerpo = json.dumps(datos).encode("utf-8")
            headers["Content-Type"] = "application/json"

        if self.csrf and metodo in ("POST", "PUT", "DELETE"):
            headers["X-CSRFToken"] = self.csrf

        peticion = Request(
            BASE + ruta,
            data=cuerpo,
            headers=headers,
            method=metodo,
        )

        try:
            with self.opener.open(peticion, timeout=20) as respuesta:
                return respuesta.status, json.load(respuesta)
        except HTTPError as exc:
            try:
                contenido = json.loads(exc.read().decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                contenido = {"error": "Respuesta HTTP no JSON"}

            return exc.code, contenido

    def preparar(self):
        codigo, datos = self.enviar(
            "GET", "/api/auth/csrf-token"
        )
        if codigo != 200:
            raise RuntimeError("No se pudo obtener CSRF.")

        self.csrf = datos["csrf_token"]

    def login(self, email):
        codigo, _ = self.enviar(
            "POST",
            "/api/auth/login",
            {"email": email, "password": PASSWORD},
        )
        return codigo


def comprobar(nombre, recibido, esperado):
    global ERRORES

    if recibido == esperado:
        print(f"OK - {nombre}: {recibido}")
    else:
        print(
            f"ERROR - {nombre}: "
            f"esperado {esperado}, recibido {recibido}"
        )
        ERRORES += 1


def registrar(nombre, rol, identificador):
    cliente = Cliente()
    cliente.preparar()

    email = (
        f"{nombre.lower()}.{identificador}"
        "@peluditos.example"
    )

    datos = {
        "nombre": nombre,
        "apellido": "Integridad",
        "email": email,
        "password": PASSWORD,
        "telefono": "3420000000",
        "provincia": "Santa Fe",
        "localidad": "Santa Fe",
        "rol": rol,
    }

    codigo, respuesta = cliente.enviar(
        "POST", "/api/auth/register", datos
    )
    comprobar(f"Registro {nombre}", codigo, 201)

    codigo = cliente.login(email)
    comprobar(f"Login {nombre}", codigo, 200)

    return cliente, email


def crear_mascotas(cliente, nombres):
    ids = []

    for nombre in nombres:
        codigo, respuesta = cliente.enviar(
            "POST",
            "/api/mascotas",
            {
                "nombre": nombre,
                "especie": "PERRO",
                "tamano": "MEDIANO",
            },
        )

        comprobar(f"Mascota {nombre}", codigo, 201)
        ids.append(respuesta["mascota"]["id"])

    return ids


def datos_solicitud(cuidador_id, inicio, salida, ids):
    return {
        "cuidador_id": cuidador_id,
        "modalidad": "ALOJAMIENTO",
        "fecha_desde": inicio,
        "fecha_hasta": salida,
        "mascotas_ids": ids,
        "contacto_emergencia": "Contacto de prueba",
        "veterinario_emergencia": "Veterinaria de prueba",
        "autorizacion_urgencia": True,
        "limite_gastos_urgencia": "5000.00",
    }


def aceptar_en_paralelo(cliente, solicitud_id, barrera):
    # Ambas tareas esperan hasta estar listas.
    barrera.wait(timeout=10)

    return cliente.enviar(
        "POST", f"/api/solicitudes/{solicitud_id}/aceptar"
    )


def main():
    identificador = uuid.uuid4().hex[:10]

    dueno_a, _ = registrar(
        "Ana", "DUENO", identificador
    )
    dueno_b, _ = registrar(
        "Beto", "DUENO", identificador
    )
    cuidador, email_cuidador = registrar(
        "Carlos", "CUIDADOR", identificador
    )

    codigo, respuesta = cuidador.enviar(
        "POST",
        "/api/cuidadores/mi-perfil",
        {
            "descripcion": "Prueba de integridad",
            "capacidad_maxima": 2,
            "admite_perros": True,
            "admite_gatos": True,
            "tarifa_diaria": "100.00",
            "tarifa_visita": "50.00",
        },
    )

    comprobar("Perfil creado", codigo, 201)
    cuidador_id = respuesta["cuidador"]["id"]

    ingreso = date.today() + timedelta(days=20)
    egreso = ingreso + timedelta(days=3)

    desde = ingreso.isoformat()
    hasta = egreso.isoformat()

    codigo, respuesta = cuidador.enviar(
        "POST",
        "/api/disponibilidades",
        {
            "modalidad": "ALOJAMIENTO",
            "fecha_desde": desde,
            "fecha_hasta": hasta,
        },
    )

    comprobar("Disponibilidad creada", codigo, 201)
    disponibilidad_id = respuesta["disponibilidad"]["id"]

    ids_a = crear_mascotas(
        dueno_a, ["Luna", "Toby"]
    )
    ids_b = crear_mascotas(
        dueno_b, ["Milo", "Rocco"]
    )

    codigo, respuesta = dueno_a.enviar(
        "POST",
        "/api/solicitudes",
        datos_solicitud(
            cuidador_id, desde, hasta, ids_a
        ),
    )
    comprobar("Solicitud A pendiente", codigo, 201)
    solicitud_a = respuesta["solicitud"]["id"]

    codigo, respuesta = dueno_b.enviar(
        "POST",
        "/api/solicitudes",
        datos_solicitud(
            cuidador_id, desde, hasta, ids_b
        ),
    )
    comprobar("Solicitud B pendiente", codigo, 201)
    solicitud_b = respuesta["solicitud"]["id"]

    # Dos sesiones HTTP independientes del mismo cuidador.
    cuidador_2 = Cliente()
    cuidador_2.preparar()
    comprobar(
        "Segundo login cuidador",
        cuidador_2.login(email_cuidador),
        200,
    )

    print("\nPRUEBA DE ACEPTACIONES SIMULTANEAS")

    barrera = Barrier(2)

    with ThreadPoolExecutor(max_workers=2) as ejecutor:
        tarea_a = ejecutor.submit(
            aceptar_en_paralelo,
            cuidador,
            solicitud_a,
            barrera,
        )
        tarea_b = ejecutor.submit(
            aceptar_en_paralelo,
            cuidador_2,
            solicitud_b,
            barrera,
        )

        codigo_a, respuesta_a = tarea_a.result()
        codigo_b, respuesta_b = tarea_b.result()

    print("Aceptacion A:", codigo_a, respuesta_a.get("error", ""))
    print("Aceptacion B:", codigo_b, respuesta_b.get("error", ""))

    codigos = sorted([codigo_a, codigo_b])
    comprobar("Una aceptada y otra rechazada", codigos, [200, 409])

    # Consultar estados persistidos.
    _, detalle_a = dueno_a.enviar(
        "GET", f"/api/solicitudes/{solicitud_a}"
    )
    _, detalle_b = dueno_b.enviar(
        "GET", f"/api/solicitudes/{solicitud_b}"
    )

    estado_a = detalle_a["solicitud"]["estado"]
    estado_b = detalle_b["solicitud"]["estado"]

    comprobar(
        "Solo una reserva aceptada",
        sorted([estado_a, estado_b]),
        ["ACEPTADA", "PENDIENTE"],
    )

    print("\nPRUEBAS DE PROTECCION")

    codigo, _ = cuidador.enviar(
        "PUT",
        "/api/cuidadores/mi-perfil",
        {"capacidad_maxima": 1},
    )
    comprobar("Reducir capacidad ocupada", codigo, 409)

    codigo, _ = cuidador.enviar(
        "PUT",
        "/api/cuidadores/mi-perfil",
        {"admite_perros": False},
    )
    comprobar("Dejar de admitir perros reservados", codigo, 409)

    codigo, _ = cuidador.enviar(
        "PUT",
        f"/api/disponibilidades/{disponibilidad_id}",
        {
            "fecha_hasta": (
                egreso + timedelta(days=1)
            ).isoformat()
        },
    )
    comprobar("Editar periodo comprometido", codigo, 409)

    codigo, _ = cuidador.enviar(
        "DELETE",
        f"/api/disponibilidades/{disponibilidad_id}",
    )
    comprobar("Desactivar periodo comprometido", codigo, 409)

    codigo, _ = cuidador.enviar(
        "PUT",
        "/api/cuidadores/mi-perfil",
        {"descripcion": "Descripcion actualizada"},
    )
    comprobar("Editar descripcion permitida", codigo, 200)

    # Cancelar solamente la reserva que fue aceptada.
    if estado_a == "ACEPTADA":
        dueno_ganador = dueno_a
        solicitud_ganadora = solicitud_a
    else:
        dueno_ganador = dueno_b
        solicitud_ganadora = solicitud_b

    codigo, _ = dueno_ganador.enviar(
        "POST",
        f"/api/solicitudes/{solicitud_ganadora}/cancelar",
    )
    comprobar("Cancelar reserva aceptada", codigo, 200)

    # Ya no hay plazas comprometidas.
    codigo, _ = cuidador.enviar(
        "PUT",
        "/api/cuidadores/mi-perfil",
        {"capacidad_maxima": 1},
    )
    comprobar("Reducir capacidad tras cancelar", codigo, 200)

    codigo, _ = cuidador.enviar(
        "PUT",
        f"/api/disponibilidades/{disponibilidad_id}",
        {
            "fecha_hasta": (
                egreso + timedelta(days=1)
            ).isoformat()
        },
    )
    comprobar("Editar periodo liberado", codigo, 200)

    print("\nRESULTADO")
    if ERRORES == 0:
        print("TODAS LAS PRUEBAS PASARON")
    else:
        print(f"FALLARON {ERRORES} PRUEBAS")
        raise SystemExit(1)

    print("Cuidador:", cuidador_id)
    print("Solicitud A:", solicitud_a)
    print("Solicitud B:", solicitud_b)


if __name__ == "__main__":
    main()
