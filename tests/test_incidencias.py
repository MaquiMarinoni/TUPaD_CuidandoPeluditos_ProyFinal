"""Pruebas aisladas de incidencias (SQLite en memoria)."""
from datetime import date, timedelta

import pytest

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import PerfilCuidador, Rol, Solicitud, Usuario


@pytest.fixture
def datos():
    app = create_app("test")
    with app.app_context():
        db.create_all()
        rd = Rol(nombre="DUENO")
        rc = Rol(nombre="CUIDADOR")
        db.session.add_all([rd, rc])
        db.session.flush()
        cuentas = []
        for nombre, rol in (("Ana", rd), ("Beto", rd), ("Carlos", rc), ("Diana", rc)):
            u = Usuario(
                nombre=nombre, apellido="Prueba", email=f"{nombre.lower()}@example.com",
                telefono="3420000000", provincia="Santa Fe", localidad="Santa Fe", rol_id=rol.id
            )
            u.set_password("PruebaSegura123")
            cuentas.append(u)
        db.session.add_all(cuentas)
        db.session.flush()
        ana, beto, carlos, diana = cuentas
        perfil = PerfilCuidador(usuario_id=carlos.id, tarifa_diaria=1000, capacidad_maxima=2)
        db.session.add(perfil)
        db.session.flush()
        hoy = date.today()
        servicio = Solicitud(
            dueno_id=ana.id, cuidador_id=perfil.id, modalidad="ALOJAMIENTO",
            fecha_desde=hoy - timedelta(days=1), fecha_hasta=hoy + timedelta(days=1),
            estado="ACEPTADA", total_mascotas=1, monto_total=2000,
            contacto_emergencia="Ficticio", autorizacion_urgencia=False
        )
        futura = Solicitud(
            dueno_id=ana.id, cuidador_id=perfil.id, modalidad="ALOJAMIENTO",
            fecha_desde=hoy + timedelta(days=5), fecha_hasta=hoy + timedelta(days=6),
            estado="ACEPTADA", total_mascotas=1, monto_total=1000,
            contacto_emergencia="Ficticio", autorizacion_urgencia=False
        )
        db.session.add_all([servicio, futura])
        db.session.commit()
        ids = {"servicio": servicio.id, "futura": futura.id}
    yield app, ids
    with app.app_context():
        db.session.remove()
        db.drop_all()


def cliente(app, nombre):
    c = app.test_client()
    r = c.post("/api/auth/login", json={"email": f"{nombre.lower()}@example.com", "password": "PruebaSegura123"})
    assert r.status_code == 200
    return c


def payload(sid):
    return {"solicitud_id": sid, "tipo": "SALUD", "descripcion": "Se requirio observacion veterinaria.", "medidas_tomadas": "Se informo al dueno."}


def test_registro_consulta_y_resolucion(datos):
    app, ids = datos
    cuidador = cliente(app, "Carlos")
    duena = cliente(app, "Ana")
    creado = cuidador.post("/api/incidencias", json=payload(ids["servicio"]))
    assert creado.status_code == 201, creado.json
    iid = creado.json["incidencia"]["id"]
    assert creado.json["incidencia"]["estado"] == "ABIERTA"
    assert duena.get(f"/api/incidencias?solicitud_id={ids['servicio']}").json["incidencias"][0]["id"] == iid
    assert duena.get(f"/api/incidencias/{iid}").status_code == 200
    assert duena.patch(f"/api/incidencias/{iid}/resolver", json={"medidas_tomadas": "Atendida."}).status_code == 403
    cerrado = cuidador.patch(f"/api/incidencias/{iid}/resolver", json={"medidas_tomadas": "Veterinaria informada."})
    assert cerrado.status_code == 200, cerrado.json
    assert cerrado.json["incidencia"]["estado"] == "RESUELTA"
    assert cuidador.patch(f"/api/incidencias/{iid}/resolver", json={"medidas_tomadas": "Otra."}).status_code == 409


def test_prohibir_ajenos_y_dueno_reportando(datos):
    app, ids = datos
    duena = cliente(app, "Ana")
    ajeno = cliente(app, "Beto")
    otro_cuidador = cliente(app, "Diana")
    assert duena.post("/api/incidencias", json=payload(ids["servicio"])).status_code == 403
    assert ajeno.get(f"/api/incidencias?solicitud_id={ids['servicio']}").status_code == 404
    assert otro_cuidador.post("/api/incidencias", json=payload(ids["servicio"])).status_code == 404


def test_no_reportar_antes_del_servicio(datos):
    app, ids = datos
    cuidador = cliente(app, "Carlos")
    assert cuidador.post("/api/incidencias", json=payload(ids["futura"])).status_code == 409
    assert cuidador.post("/api/incidencias", json={**payload(ids["servicio"]), "tipo": "INVALIDO"}).status_code == 400
    assert cuidador.post("/api/incidencias", json={**payload(ids["servicio"]), "estado": "RESUELTA"}).status_code == 400


def test_requiere_sesion(datos):
    app, ids = datos
    anonimo = app.test_client()
    assert anonimo.get(f"/api/incidencias?solicitud_id={ids['servicio']}").status_code == 401
    assert anonimo.post("/api/incidencias", json=payload(ids["servicio"])).status_code == 401
