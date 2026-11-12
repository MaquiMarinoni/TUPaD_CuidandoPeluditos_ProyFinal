
from datetime import date, timedelta
from http.cookiejar import CookieJar
from urllib.error import HTTPError
from urllib.request import Request, HTTPCookieProcessor, build_opener
import json
import os
import uuid


BASE = os.environ.get("PELUDITOS_TEST_URL", "http://127.0.0.1:5000").rstrip("/")
PASSWORD = "PruebaLocal2026!"
fallas = 0


class Cliente:
    def __init__(self):
        self.opener = build_opener(HTTPCookieProcessor(CookieJar()))
        self.token = None

    def enviar(self, metodo, ruta, datos=None, sin_csrf=False):
        headers = {}
        cuerpo = None

        if datos is not None:
            headers["Content-Type"] = "application/json"
            cuerpo = json.dumps(datos).encode("utf-8")

        if self.token and not sin_csrf:
            headers["X-CSRFToken"] = self.token

        peticion = Request(
            BASE + ruta,
            data=cuerpo,
            headers=headers,
            method=metodo,
        )

        try:
            with self.opener.open(peticion, timeout=20) as respuesta:
                texto = respuesta.read().decode("utf-8")
                return respuesta.status, json.loads(texto)
        except HTTPError as exc:
            texto = exc.read().decode("utf-8")
            try:
                datos_error = json.loads(texto)
            except ValueError:
                datos_error = {"error": texto}
            return exc.code, datos_error

    def preparar(self):
        codigo, respuesta = self.enviar(
            "GET", "/api/auth/csrf-token"
        )
        comprobar("Obtener CSRF", codigo, 200)
        self.token = respuesta["csrf_token"]


def comprobar(nombre, obtenido, esperado):
    global fallas

    if obtenido == esperado:
        print(f"OK - {nombre}: {obtenido}")
    else:
        print(
            f"ERROR - {nombre}: "
            f"esperado {esperado}, recibido {obtenido}"
        )
        fallas += 1


def usuario(nombre, rol, identificador):
    cliente = Cliente()
    cliente.preparar()

    email = f"{nombre.lower()}.{identificador}@peluditos.example"

    codigo, _ = cliente.enviar("POST", "/api/auth/register", {
        "nombre": nombre,
        "apellido": "Visitas",
        "email": email,
        "password": PASSWORD,
        "telefono": "3420000000",
        "provincia": "Santa Fe",
        "localidad": "Santa Fe",
        "rol": rol,
    })
    comprobar(f"Registrar {nombre}", codigo, 201)

    codigo, _ = cliente.enviar("POST", "/api/auth/login", {
        "email": email,
        "password": PASSWORD,
    })
    comprobar(f"Login {nombre}", codigo, 200)

    return cliente


def mascota(cliente, nombre):
    codigo, respuesta = cliente.enviar(
        "POST", "/api/mascotas", {
            "nombre": nombre,
            "especie": "PERRO",
            "tamano": "MEDIANO",
        }
    )
    comprobar(f"Crear mascota {nombre}", codigo, 201)
    return respuesta["mascota"]["id"]


def datos_visita(cuidador_id, fecha, inicio, fin, ids):
    return {
        "cuidador_id": cuidador_id,
        "fecha": fecha,
        "hora_desde": inicio,
        "hora_hasta": fin,
        "mascotas_ids": ids,
        "direccion_servicio": "Domicilio ficticio de prueba",
        "contacto_emergencia": "Contacto de prueba",
        "veterinario_emergencia": "Veterinaria de prueba",
        "autorizacion_urgencia": True,
        "limite_gastos_urgencia": "5000.00",
    }


def main():
    identificador = uuid.uuid4().hex[:10]

    ana = usuario("Ana", "DUENO", identificador)
    beto = usuario("Beto", "DUENO", identificador)
    carlos = usuario("Carlos", "CUIDADOR", identificador)

    codigo, perfil = carlos.enviar(
        "POST", "/api/cuidadores/mi-perfil", {
            "descripcion": "Prueba de visitas",
            "capacidad_maxima": 2,
            "admite_perros": True,
            "admite_gatos": True,
            "tarifa_diaria": "100.00",
            "tarifa_visita": "80.00",
        }
    )
    comprobar("Crear perfil cuidador", codigo, 201)
    cuidador_id = perfil["cuidador"]["id"]

    fecha = (date.today() + timedelta(days=20)).isoformat()

    codigo, disponibilidad = carlos.enviar(
        "POST", "/api/disponibilidades", {
            "modalidad": "VISITA",
            "fecha_desde": fecha,
            "fecha_hasta": fecha,
            "hora_desde": "09:00",
            "hora_hasta": "15:00",
        }
    )
    comprobar("Crear disponibilidad visita", codigo, 201)
    disponibilidad_id = disponibilidad["disponibilidad"]["id"]

    luna = mascota(ana, "Luna")
    toby = mascota(ana, "Toby")
    milo = mascota(beto, "Milo")

    datos_ana = datos_visita(
        cuidador_id, fecha, "10:00", "11:30",
        [luna, toby]
    )

    codigo, respuesta = ana.enviar(
        "POST", "/api/visitas", datos_ana
    )
    comprobar("Crear visita con dos mascotas", codigo, 201)

    visita_ana = respuesta["solicitud"]["id"]

    comprobar(
        "Modalidad de la solicitud",
        respuesta["solicitud"]["modalidad"],
        "VISITA",
    )
    comprobar(
        "Precio por turno",
        float(respuesta["solicitud"]["monto_total"]),
        80.0,
    )
    comprobar(
        "Cantidad de mascotas",
        respuesta["solicitud"]["total_mascotas"],
        2,
    )
    comprobar(
        "Direccion historica",
        respuesta["solicitud"]["direccion_servicio"],
        "Domicilio ficticio de prueba",
    )

    # Otra solicitud puede quedar pendiente.
    datos_beto = datos_visita(
        cuidador_id, fecha, "11:00", "12:00", [milo]
    )

    codigo, respuesta = beto.enviar(
        "POST", "/api/visitas", datos_beto
    )
    comprobar("Segunda solicitud pendiente", codigo, 201)
    visita_beto = respuesta["solicitud"]["id"]

    # Aceptar la primera.
    codigo, respuesta = carlos.enviar(
        "POST", f"/api/solicitudes/{visita_ana}/aceptar"
    )
    comprobar("Aceptar visita Ana", codigo, 200)
    comprobar(
        "Estado aceptado",
        respuesta["solicitud"]["estado"],
        "ACEPTADA",
    )

    # La segunda se superpone entre 11:00 y 11:30.
    codigo, _ = carlos.enviar(
        "POST", f"/api/solicitudes/{visita_beto}/aceptar"
    )
    comprobar("Rechazar visita superpuesta", codigo, 409)

    # Proteger la franja que respalda la reserva.
    codigo, _ = carlos.enviar(
        "DELETE", f"/api/disponibilidades/{disponibilidad_id}"
    )
    comprobar("Impedir desactivar franja comprometida", codigo, 409)

    # El otro dueño no puede consultar la visita ajena.
    codigo, _ = beto.enviar(
        "GET", f"/api/solicitudes/{visita_ana}"
    )
    comprobar("Privacidad de la solicitud", codigo, 404)

    # No admitir la mascota de otro dueño.
    datos_ajenos = datos_visita(
        cuidador_id, fecha, "13:00", "14:00", [luna]
    )
    codigo, _ = beto.enviar(
        "POST", "/api/visitas", datos_ajenos
    )
    comprobar("Rechazar mascota ajena", codigo, 403)

    # Fuera de horario publicado.
    fuera_de_horario = datos_visita(
        cuidador_id, fecha, "16:00", "17:00", [milo]
    )
    codigo, _ = beto.enviar(
        "POST", "/api/visitas", fuera_de_horario
    )
    comprobar("Rechazar horario fuera de disponibilidad", codigo, 409)

    # Validar horarios invertidos.
    horario_invalido = datos_visita(
        cuidador_id, fecha, "14:00", "12:00", [milo]
    )
    codigo, _ = beto.enviar(
        "POST", "/api/visitas", horario_invalido
    )
    comprobar("Rechazar horario invertido", codigo, 400)

    # Debe exigir direccion exacta del servicio.
    sin_direccion = datos_visita(
        cuidador_id, fecha, "13:00", "14:00", [milo]
    )
    del sin_direccion["direccion_servicio"]

    codigo, _ = beto.enviar(
        "POST", "/api/visitas", sin_direccion
    )
    comprobar("Exigir direccion", codigo, 400)

    # CSRF ausente en una peticion autenticada.
    codigo, _ = ana.enviar(
        "POST", "/api/visitas",
        datos_ana, sin_csrf=True
    )
    comprobar("Proteccion CSRF", codigo, 400)

    # Una visita futura aceptada no se puede finalizar.
    codigo, _ = carlos.enviar(
        "POST", f"/api/solicitudes/{visita_ana}/finalizar"
    )
    comprobar("Impedir finalizacion anticipada", codigo, 409)

    # Cancelar para liberar el turno.
    codigo, _ = ana.enviar(
        "POST", f"/api/solicitudes/{visita_ana}/cancelar"
    )
    comprobar("Cancelar visita aceptada", codigo, 200)

    # Ahora se puede aceptar la segunda.
    codigo, _ = carlos.enviar(
        "POST", f"/api/solicitudes/{visita_beto}/aceptar"
    )
    comprobar("Aceptar visita tras liberar turno", codigo, 200)

    codigo, detalle = beto.enviar(
        "GET", f"/api/solicitudes/{visita_beto}"
    )
    comprobar("Consultar detalle", codigo, 200)
    comprobar(
        "Historial conservado",
        len(detalle["solicitud"]["historial"]),
        2,
    )

    print("\nRESULTADO:")
    if fallas:
        print(f"FALLARON {fallas} PRUEBAS")
        raise SystemExit(1)

    print("TODAS LAS PRUEBAS PASARON")
    print("Cuidador:", cuidador_id)
    print("Visita Ana:", visita_ana)
    print("Visita Beto:", visita_beto)


if __name__ == "__main__":
    main()
