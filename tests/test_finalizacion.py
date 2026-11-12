"""Finalizacion de un servicio historico ficticio en SQLite en memoria.

No modifica MariaDB ni el reloj. No sustituye la prueba HTTP de MariaDB.
"""
from datetime import date, timedelta
import pytest
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import Rol, Usuario, PerfilCuidador, Mascota, Solicitud, SolicitudMascota, HistorialEstado


@pytest.fixture
def servicio_historico():
    app = create_app("test")
    with app.app_context():
        db.create_all()
        dueno_rol = Rol(nombre="DUENO")
        cuidador_rol = Rol(nombre="CUIDADOR")
        db.session.add_all([dueno_rol, cuidador_rol])
        db.session.flush()
        usuarios = []
        for nombre, rol in (("Dueno", dueno_rol), ("Cuidador", cuidador_rol)):
            u = Usuario(nombre=nombre, apellido="Historico", email=f"{nombre.lower()}@example.com", telefono="000", provincia="Santa Fe", localidad="Rosario", rol_id=rol.id)
            u.set_password("PruebaLocal2026!")
            usuarios.append(u)
        db.session.add_all(usuarios)
        db.session.flush()
        dueno, cuidador = usuarios
        perfil = PerfilCuidador(usuario_id=cuidador.id, capacidad_maxima=1, tarifa_diaria=100, admite_perros=True, admite_gatos=False)
        mascota = Mascota(dueno_id=dueno.id, nombre="Historica", especie="PERRO", tamano="CHICO")
        db.session.add_all([perfil, mascota])
        db.session.flush()
        solicitud = Solicitud(dueno_id=dueno.id, cuidador_id=perfil.id, modalidad="ALOJAMIENTO", fecha_desde=date.today()-timedelta(days=3), fecha_hasta=date.today()-timedelta(days=1), estado="ACEPTADA", total_mascotas=1, monto_total=200, contacto_emergencia="Ficticio", autorizacion_urgencia=False)
        solicitud.mascotas_asociadas.append(SolicitudMascota(mascota_id=mascota.id, nombre_snapshot="Historica", especie_snapshot="PERRO"))
        db.session.add(solicitud)
        db.session.flush()
        db.session.add_all([
            HistorialEstado(solicitud_id=solicitud.id, usuario_id=dueno.id, estado_anterior=None, estado_nuevo="PENDIENTE"),
            HistorialEstado(solicitud_id=solicitud.id, usuario_id=cuidador.id, estado_anterior="PENDIENTE", estado_nuevo="ACEPTADA"),
        ])
        db.session.commit()
        solicitud_id = solicitud.id
    yield app, solicitud_id
    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_finalizar_servicio_historico_y_rechazar_repeticion(servicio_historico):
    app, sid = servicio_historico
    cliente = app.test_client()
    login = cliente.post("/api/auth/login", json={"email":"cuidador@example.com", "password":"PruebaLocal2026!"})
    assert login.status_code == 200
    respuesta = cliente.post(f"/api/solicitudes/{sid}/finalizar")
    assert respuesta.status_code == 200
    assert respuesta.json["solicitud"]["estado"] == "FINALIZADA"
    detalle = cliente.get(f"/api/solicitudes/{sid}").json["solicitud"]
    assert [h["estado_nuevo"] for h in detalle["historial"]] == ["PENDIENTE", "ACEPTADA", "FINALIZADA"]
    assert cliente.post(f"/api/solicitudes/{sid}/finalizar").status_code == 409
    with app.app_context():
        assert db.session.get(Solicitud, sid).estado == "FINALIZADA"
