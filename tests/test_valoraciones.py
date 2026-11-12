"""Pruebas de valoraciones verificadas en SQLite temporal (no MariaDB)."""
from datetime import date, timedelta

import pytest

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import Rol, Usuario, PerfilCuidador, Solicitud, Valoracion


@pytest.fixture
def escenario():
    app = create_app("test")
    with app.app_context():
        db.create_all()
        roles = {nombre: Rol(nombre=nombre) for nombre in ("DUENO", "CUIDADOR")}
        db.session.add_all(roles.values())
        db.session.flush()
        usuarios = {}
        for nombre, rol in (("ana", "DUENO"), ("beto", "DUENO"), ("carlos", "CUIDADOR")):
            u = Usuario(
                nombre=nombre, apellido="Prueba", email=f"{nombre}@example.com",
                telefono="000", provincia="Santa Fe", localidad="Santa Fe",
                rol_id=roles[rol].id,
            )
            u.set_password("PruebaLocal2026!")
            db.session.add(u)
            usuarios[nombre] = u
        db.session.flush()
        perfil = PerfilCuidador(
            usuario_id=usuarios["carlos"].id, capacidad_maxima=2,
            tarifa_diaria=100, admite_perros=True, admite_gatos=True,
        )
        db.session.add(perfil)
        db.session.flush()
        solicitud_final = Solicitud(
            dueno_id=usuarios["ana"].id, cuidador_id=perfil.id,
            modalidad="ALOJAMIENTO", fecha_desde=date.today()-timedelta(days=4),
            fecha_hasta=date.today()-timedelta(days=2), estado="FINALIZADA",
            total_mascotas=1, monto_total=200, contacto_emergencia="Contacto ficticio",
            autorizacion_urgencia=False,
        )
        solicitud_pendiente = Solicitud(
            dueno_id=usuarios["ana"].id, cuidador_id=perfil.id,
            modalidad="ALOJAMIENTO", fecha_desde=date.today()+timedelta(days=2),
            fecha_hasta=date.today()+timedelta(days=3), estado="PENDIENTE",
            total_mascotas=1, monto_total=100, contacto_emergencia="Contacto ficticio",
            autorizacion_urgencia=False,
        )
        db.session.add_all([solicitud_final, solicitud_pendiente])
        db.session.commit()
        ids = {"final": solicitud_final.id, "pendiente": solicitud_pendiente.id, "cuidador": perfil.id}
    yield app, ids
    with app.app_context():
        db.session.remove()
        db.drop_all()


def ingresar(cliente, nombre):
    resultado = cliente.post("/api/auth/login", json={
        "email": f"{nombre}@example.com", "password": "PruebaLocal2026!",
    })
    assert resultado.status_code == 200


def test_dueno_valora_servicio_finalizado_y_se_calcula_promedio(escenario):
    app, ids = escenario
    cliente = app.test_client()
    ingresar(cliente, "ana")
    respuesta = cliente.post("/api/valoraciones", json={
        "solicitud_id": ids["final"], "puntaje": 5, "comentario": "Buen servicio",
    })
    assert respuesta.status_code == 201, respuesta.json
    assert respuesta.json["valoracion"]["puntaje"] == 5
    listado = cliente.get(f"/api/valoraciones?cuidador_id={ids['cuidador']}")
    assert listado.status_code == 200
    assert listado.json["resumen"]["cantidad"] == 1
    assert listado.json["resumen"]["promedio"] == 5.0
    resumen = cliente.get(f"/api/valoraciones/resumen/{ids['cuidador']}")
    assert resumen.json["resumen"]["cantidad"] == 1


def test_no_se_puede_valorar_dos_veces(escenario):
    app, ids = escenario
    cliente = app.test_client()
    ingresar(cliente, "ana")
    datos = {"solicitud_id": ids["final"], "puntaje": 4}
    assert cliente.post("/api/valoraciones", json=datos).status_code == 201
    assert cliente.post("/api/valoraciones", json=datos).status_code == 409
    with app.app_context():
        assert Valoracion.query.count() == 1


def test_prohibido_ajena_pendiente_y_cuidador(escenario):
    app, ids = escenario
    ajeno = app.test_client()
    ingresar(ajeno, "beto")
    assert ajeno.post("/api/valoraciones", json={"solicitud_id": ids["final"], "puntaje": 5}).status_code == 404
    cuidador = app.test_client()
    ingresar(cuidador, "carlos")
    assert cuidador.post("/api/valoraciones", json={"solicitud_id": ids["final"], "puntaje": 5}).status_code == 403
    dueno = app.test_client()
    ingresar(dueno, "ana")
    assert dueno.post("/api/valoraciones", json={"solicitud_id": ids["pendiente"], "puntaje": 5}).status_code == 409
    assert app.test_client().post("/api/valoraciones", json={"solicitud_id": ids["final"], "puntaje": 5}).status_code == 401


def test_validaciones_y_resumen_sin_resenas(escenario):
    app, ids = escenario
    cliente = app.test_client()
    vacio = cliente.get(f"/api/valoraciones/resumen/{ids['cuidador']}")
    assert vacio.json["resumen"] == {"cuidador_id": ids["cuidador"], "cantidad": 0, "promedio": None}
    ingresar(cliente, "ana")
    for puntaje in (0, 6, 2.5, True, "5"):
        assert cliente.post("/api/valoraciones", json={"solicitud_id": ids["final"], "puntaje": puntaje}).status_code == 400
    assert cliente.post("/api/valoraciones", json={"solicitud_id": ids["final"], "puntaje": 5, "dueno_id": 1}).status_code == 400
    assert cliente.post("/api/valoraciones", json={"solicitud_id": ids["final"], "puntaje": 5, "comentario": "x"*2001}).status_code == 400
