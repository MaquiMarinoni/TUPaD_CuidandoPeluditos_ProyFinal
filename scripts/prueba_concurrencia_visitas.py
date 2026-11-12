
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
import os
import uuid


# Permite elegir la instancia local sin cambiar la prueba.
BASE = os.environ.get("PELUDITOS_TEST_URL", "http://127.0.0.1:5000").rstrip("/")
PASSWORD = "PruebaLocal2026!"
fallas = 0


class Cliente:
    def __init__(self):
        self.opener = build_opener(
            HTTPCookieProcessor(CookieJar())
        )
        self.token = None

    def enviar(self, metodo, ruta, datos=None, con_csrf=True):
        headers = {}
        cuerpo = None

        if datos is not None:
            cuerpo = json.dumps(datos).encode("utf-8")
            headers["Content-Type"] = "application/json"

        if self.token and con_csrf:
            headers["X-CSRFToken"] = self.token

        peticion = Request(
            BASE + ruta,
            method=metodo,
            data=cuerpo,
            headers=headers,
        )

        try:
            with self.opener.open(peticion, timeout=30) as respuesta:
                contenido = respuesta.read().decode("utf-8")
                return respuesta.status, json.loads(contenido)

        except HTTPError as exc:
            contenido = exc.read().decode("utf-8")

            try:
                respuesta = json.loads(contenido)
            except ValueError:
                respuesta = {"error": contenido}

            return exc.code, respuesta

    def preparar(self):
        codigo, respuesta = self.enviar(
            "GET", "/api/auth/csrf-token"
        )

        verificar("Obtener token CSRF", codigo, 200)
        self.token = respuesta["csrf_token"]


def verificar(nombre, obtenido, esperado):
    global fallas

    if obtenido == esperado:
        print(f"OK - {nombre}: {obtenido}")
    else:
        print(
            f"ERROR - {nombre}: "
            f"esperado {esperado}, obtenido {obtenido}"
        )
        fallas += 1


def crear_usuario(nombre, rol, identificador):
    cliente = Cliente()
    cliente.preparar()

    email = (
        f"{nombre.lower()}.{identificador}"
        "@peluditos.example"
    )

    codigo, _ = cliente.enviar(
        "POST",
        "/api/auth/register",
        {
            "nombre": nombre,
            "apellido": "Auditoria",
            "email": email,
            "password": PASSWORD,
            "telefono": "3420000000",
            "provincia": "Santa Fe",
            "localidad": "Santa Fe",
            "rol": rol,
        },
    )
    verificar(f"Registro {nombre}", codigo, 201)

    codigo, _ = cliente.enviar(
        "POST",
        "/api/auth/login",
        {"email": email, "password": PASSWORD},
    )
    verificar(f"Login {nombre}", codigo, 200)

    return cliente, email


def crear_mascota(cliente, nombre):
    codigo, respuesta = cliente.enviar(
        "POST",
        "/api/mascotas",
        {
            "nombre": nombre,
            "especie": "PERRO",
            "tamano": "MEDIANO",
        },
    )

    verificar(f"Crear mascota {nombre}", codigo, 201)
    return respuesta["mascota"]["id"]


def datos_visita(cuidador_id, fecha, mascota_id, inicio, fin):
    return {
        "cuidador_id": cuidador_id,
        "fecha": fecha,
        "hora_desde": inicio,
        "hora_hasta": fin,
        "mascotas_ids": [mascota_id],
        "direccion_servicio": "Domicilio ficticio de auditoria",
        "contacto_emergencia": "Contacto de auditoria",
        "veterinario_emergencia": "Veterinaria de prueba",
        "autorizacion_urgencia": True,
        "limite_gastos_urgencia": "5000.00",
    }


def aceptar_simultaneamente(cliente, solicitud_id, barrera):
    barrera.wait(timeout=15)

    return cliente.enviar(
        "POST",
        f"/api/solicitudes/{solicitud_id}/aceptar",
    )


def main():
    identificador = uuid.uuid4().hex[:10]

    ana, _ = crear_usuario(
        "Ana", "DUENO", identificador
    )
    beto, _ = crear_usuario(
        "Beto", "DUENO", identificador
    )
    carlos, email_carlos = crear_usuario(
        "Carlos", "CUIDADOR", identificador
    )

    codigo, respuesta = carlos.enviar(
        "POST",
        "/api/cuidadores/mi-perfil",
        {
            "descripcion": "Auditoria de concurrencia",
            "capacidad_maxima": 2,
            "admite_perros": True,
            "admite_gatos": True,
            "tarifa_diaria": "100.00",
            "tarifa_visita": "80.00",
        },
    )

    verificar("Crear perfil cuidador", codigo, 201)
    cuidador_id = respuesta["cuidador"]["id"]

    fecha = date.today() + timedelta(days=20)
    fecha_texto = fecha.isoformat()
    salida_texto = (fecha + timedelta(days=2)).isoformat()

    codigo, respuesta = carlos.enviar(
        "POST",
        "/api/disponibilidades",
        {
            "modalidad": "VISITA",
            "fecha_desde": fecha_texto,
            "fecha_hasta": fecha_texto,
            "hora_desde": "09:00",
            "hora_hasta": "15:00",
        },
    )

    verificar("Disponibilidad para visitas", codigo, 201)
    disponibilidad_id = respuesta["disponibilidad"]["id"]

    # Publicamos tambien alojamiento para probar
    # conflictos entre modalidades.
    codigo, _ = carlos.enviar(
        "POST",
        "/api/disponibilidades",
        {
            "modalidad": "ALOJAMIENTO",
            "fecha_desde": fecha_texto,
            "fecha_hasta": salida_texto,
        },
    )

    verificar("Disponibilidad alojamiento", codigo, 201)

    luna = crear_mascota(ana, "Luna")
    milo = crear_mascota(beto, "Milo")

    visita_ana = datos_visita(
        cuidador_id, fecha_texto, luna, "10:00", "11:30"
    )

    visita_beto = datos_visita(
        cuidador_id, fecha_texto, milo, "11:00", "12:00"
    )

    codigo, respuesta = ana.enviar(
        "POST", "/api/visitas", visita_ana
    )
    verificar("Solicitud de Ana", codigo, 201)
    id_ana = respuesta["solicitud"]["id"]

    codigo, respuesta = beto.enviar(
        "POST", "/api/visitas", visita_beto
    )
    verificar("Solicitud de Beto", codigo, 201)
    id_beto = respuesta["solicitud"]["id"]

    # Dos sesiones independientes del mismo cuidador.
    carlos_segunda_sesion = Cliente()
    carlos_segunda_sesion.preparar()

    codigo, _ = carlos_segunda_sesion.enviar(
        "POST",
        "/api/auth/login",
        {
            "email": email_carlos,
            "password": PASSWORD,
        },
    )
    verificar("Segunda sesion cuidador", codigo, 200)

    print("\n=== CONCURRENCIA DE VISITAS ===")

    barrera = Barrier(2)

    with ThreadPoolExecutor(max_workers=2) as ejecutor:
        tarea_ana = ejecutor.submit(
            aceptar_simultaneamente,
            carlos,
            id_ana,
            barrera,
        )
        tarea_beto = ejecutor.submit(
            aceptar_simultaneamente,
            carlos_segunda_sesion,
            id_beto,
            barrera,
        )

        codigo_ana, _ = tarea_ana.result()
        codigo_beto, _ = tarea_beto.result()

    print("Aceptacion Ana:", codigo_ana)
    print("Aceptacion Beto:", codigo_beto)

    verificar(
        "Una aceptacion y un rechazo",
        sorted([codigo_ana, codigo_beto]),
        [200, 409],
    )

    _, detalle_ana = ana.enviar(
        "GET", f"/api/solicitudes/{id_ana}"
    )
    _, detalle_beto = beto.enviar(
        "GET", f"/api/solicitudes/{id_beto}"
    )

    estado_ana = detalle_ana["solicitud"]["estado"]
    estado_beto = detalle_beto["solicitud"]["estado"]

    verificar(
        "Estados persistidos",
        sorted([estado_ana, estado_beto]),
        ["ACEPTADA", "PENDIENTE"],
    )

    if estado_ana == "ACEPTADA":
        dueno_ganador = ana
        mascota_ganadora = luna
        solicitud_ganadora = id_ana
    else:
        dueno_ganador = beto
        mascota_ganadora = milo
        solicitud_ganadora = id_beto

    print("\n=== SEGURIDAD Y PERMISOS ===")

    codigo, _ = beto.enviar(
        "GET", f"/api/solicitudes/{id_ana}"
    )
    verificar("Lectura de solicitud ajena", codigo, 404)

    codigo, _ = ana.enviar(
        "GET", f"/api/solicitudes/{id_beto}"
    )
    verificar("Lectura inversa de solicitud ajena", codigo, 404)

    codigo, _ = carlos.enviar(
        "POST",
        "/api/visitas",
        visita_ana,
    )
    verificar("Cuidador no puede crear visita", codigo, 403)

    codigo, _ = beto.enviar(
        "POST",
        "/api/visitas",
        datos_visita(
            cuidador_id,
            fecha_texto,
            luna,
            "13:00",
            "14:00",
        ),
    )
    verificar("Mascota de otro dueño", codigo, 403)

    codigo, _ = ana.enviar(
        "POST",
        "/api/visitas",
        visita_ana,
        con_csrf=False,
    )
    verificar("Proteccion CSRF", codigo, 400)

    codigo, _ = carlos.enviar(
        "DELETE",
        f"/api/disponibilidades/{disponibilidad_id}",
    )
    verificar(
        "Disponibilidad comprometida protegida",
        codigo,
        409,
    )

    print("\n=== CONFLICTO ENTRE MODALIDADES ===")

    alojamiento = {
        "cuidador_id": cuidador_id,
        "modalidad": "ALOJAMIENTO",
        "fecha_desde": fecha_texto,
        "fecha_hasta": salida_texto,
        "mascotas_ids": [mascota_ganadora],
        "contacto_emergencia": "Contacto de auditoria",
        "veterinario_emergencia": "Veterinaria de prueba",
        "autorizacion_urgencia": True,
        "limite_gastos_urgencia": "5000.00",
    }

    codigo, _ = dueno_ganador.enviar(
        "POST",
        "/api/solicitudes",
        alojamiento,
    )
    verificar(
        "Alojamiento de mascota con visita aceptada",
        codigo,
        409,
    )

    print("\n=== LIBERACION DEL TURNO ===")

    codigo, _ = dueno_ganador.enviar(
        "POST",
        f"/api/solicitudes/{solicitud_ganadora}/cancelar",
    )
    verificar("Cancelar visita aceptada", codigo, 200)

    codigo, _ = carlos.enviar(
        "DELETE",
        f"/api/disponibilidades/{disponibilidad_id}",
    )
    verificar(
        "Desactivar disponibilidad despues de cancelar",
        codigo,
        200,
    )

    print("\n=== RESULTADO FINAL ===")

    if fallas == 0:
        print("TODAS LAS PRUEBAS PASARON")
    else:
        print(f"FALLARON {fallas} PRUEBAS")
        raise SystemExit(1)

    print("Cuidador:", cuidador_id)
    print("Solicitud Ana:", id_ana)
    print("Solicitud Beto:", id_beto)


if __name__ == "__main__":
    main()
