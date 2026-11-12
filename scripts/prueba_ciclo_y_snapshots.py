"""Casos complementarios por HTTP contra una base local de prueba.

Crea datos ficticios propios; no modifica los creados manualmente.
Uso: PELUDITOS_TEST_URL=http://127.0.0.1:5001 python -m scripts.prueba_ciclo_y_snapshots
"""
from datetime import date, timedelta
import json
import os
import uuid
from http.cookiejar import CookieJar
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import HTTPCookieProcessor, Request, build_opener

BASE = os.environ.get("PELUDITOS_TEST_URL", "http://127.0.0.1:5001").rstrip("/")
PASSWORD = "PruebaLocal2026!"


def comprobar(nombre, obtenido, esperado):
    if obtenido != esperado:
        raise AssertionError(f"{nombre}: esperado {esperado!r}, recibido {obtenido!r}")
    print(f"OK - {nombre}: {obtenido}")


class Cliente:
    def __init__(self):
        self.opener = build_opener(HTTPCookieProcessor(CookieJar()))
        self.token = self.enviar("GET", "/api/auth/csrf-token", esperado=200)["csrf_token"]

    def enviar(self, metodo, ruta, datos=None, esperado=200):
        headers = {"Accept": "application/json"}
        if hasattr(self, "token"):
            headers["X-CSRFToken"] = self.token
        cuerpo = None
        if datos is not None:
            cuerpo = json.dumps(datos).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = Request(BASE + ruta, data=cuerpo, headers=headers, method=metodo)
        try:
            with self.opener.open(req, timeout=30) as r:
                codigo, respuesta = r.status, json.load(r)
        except HTTPError as e:
            codigo, respuesta = e.code, json.load(e)
        comprobar(f"{metodo} {ruta}", codigo, esperado)
        return respuesta


def usuario(nombre, rol, identificador):
    c = Cliente()
    email = f"{nombre}.{identificador}@peluditos.example"
    c.enviar("POST", "/api/auth/register", {
        "nombre": nombre, "apellido": "Ciclo", "email": email, "password": PASSWORD,
        "telefono": "0000000000", "provincia": "Santa Fe", "localidad": "Rosario", "rol": rol,
    }, esperado=201)
    c.enviar("POST", "/api/auth/login", {"email": email, "password": PASSWORD})
    return c


def main():
    if urlparse(BASE).hostname not in ("127.0.0.1", "localhost", "::1"):
        raise SystemExit("Esta prueba solo admite un servidor local de desarrollo.")
    identificador = uuid.uuid4().hex[:10]
    dueno = usuario("DuenoCiclo", "DUENO", identificador)
    cuidador = usuario("CuidadorCiclo", "CUIDADOR", identificador)
    perfil = cuidador.enviar("POST", "/api/cuidadores/mi-perfil", {
        "descripcion": "Perfil ficticio para pruebas de ciclo",
        "capacidad_maxima": 2, "admite_perros": True, "admite_gatos": False,
        "tarifa_diaria": "100.00", "tarifa_visita": "80.00",
    }, esperado=201)["cuidador"]["id"]
    inicio = (date.today() + timedelta(days=25)).isoformat()
    salida = (date.today() + timedelta(days=27)).isoformat()
    cuidador.enviar("POST", "/api/disponibilidades", {
        "modalidad": "ALOJAMIENTO", "fecha_desde": inicio, "fecha_hasta": salida,
    }, esperado=201)
    perro = dueno.enviar("POST", "/api/mascotas", {
        "nombre": "Perro Historico", "especie": "PERRO", "tamano": "CHICO",
        "cuidados_especiales": "Indicaciones originales", "contacto_veterinario": "Veterinario original",
    }, esperado=201)["mascota"]["id"]
    gato = dueno.enviar("POST", "/api/mascotas", {
        "nombre": "Gato Ciclo", "especie": "GATO", "tamano": "CHICO",
    }, esperado=201)["mascota"]["id"]
    base = {
        "cuidador_id": perfil, "modalidad": "ALOJAMIENTO", "fecha_desde": inicio,
        "fecha_hasta": salida, "mascotas_ids": [perro],
        "contacto_emergencia": "Contacto ficticio", "autorizacion_urgencia": False,
    }
    dueno.enviar("POST", "/api/solicitudes", {**base, "mascotas_ids": [gato]}, esperado=400)
    dueno.enviar("POST", "/api/solicitudes", {**base, "fecha_hasta": inicio}, esperado=400)
    dueno.enviar("POST", "/api/solicitudes", {**base, "autorizacion_urgencia": True}, esperado=400)
    rechazo = dueno.enviar("POST", "/api/solicitudes", base, esperado=201)["solicitud"]["id"]
    cuidador.enviar("POST", f"/api/solicitudes/{rechazo}/rechazar")
    detalle = dueno.enviar("GET", f"/api/solicitudes/{rechazo}")["solicitud"]
    comprobar("Rechazo guardado", detalle["estado"], "RECHAZADA")
    comprobar("Historial de rechazo", [h["estado_nuevo"] for h in detalle["historial"]], ["PENDIENTE", "RECHAZADA"])
    cuidador.enviar("POST", f"/api/solicitudes/{rechazo}/aceptar", esperado=409)
    autorizada = {**base, "autorizacion_urgencia": True, "veterinario_emergencia": "Veterinaria ficticia", "limite_gastos_urgencia": "5000.00"}
    reserva = dueno.enviar("POST", "/api/solicitudes", autorizada, esperado=201)["solicitud"]["id"]
    cuidador.enviar("POST", f"/api/solicitudes/{reserva}/aceptar")
    dueno.enviar("PUT", f"/api/mascotas/{perro}", {
        "nombre": "Nombre nuevo", "cuidados_especiales": "Indicaciones nuevas",
        "contacto_veterinario": "Veterinario nuevo",
    })
    actual = dueno.enviar("GET", f"/api/mascotas/{perro}")["mascota"]
    comprobar("Edicion vigente", actual["nombre"], "Nombre nuevo")
    detalle = cuidador.enviar("GET", f"/api/solicitudes/{reserva}")["solicitud"]
    snapshot = detalle["mascotas"][0]
    comprobar("Nombre historico conservado", snapshot["nombre"], "Perro Historico")
    comprobar("Cuidados historicos conservados", snapshot["cuidados_especiales"], "Indicaciones originales")
    comprobar("Veterinario historico conservado", snapshot["contacto_veterinario"], "Veterinario original")
    comprobar("Urgencias autorizadas", detalle["autorizacion_urgencia"], True)
    comprobar("Limite de urgencias guardado", float(detalle["limite_gastos_urgencia"]), 5000.0)
    cuidador.enviar("POST", f"/api/solicitudes/{reserva}/finalizar", esperado=409)
    dueno.enviar("POST", f"/api/solicitudes/{reserva}/cancelar")
    dueno.enviar("DELETE", f"/api/mascotas/{perro}")
    listado = dueno.enviar("GET", "/api/mascotas")["mascotas"]
    comprobar("Baja excluida del listado", any(m["id"] == perro for m in listado), False)
    dueno.enviar("GET", f"/api/mascotas/{perro}", esperado=404)
    detalle = dueno.enviar("GET", f"/api/solicitudes/{reserva}")["solicitud"]
    comprobar("Historial conservado tras baja", detalle["mascotas"][0]["nombre"], "Perro Historico")
    print("\nTODAS LAS PRUEBAS PASARON")
    print(f"Cuidador: {perfil}; solicitud rechazada: {rechazo}; solicitud cancelada: {reserva}")


if __name__ == "__main__":
    main()
