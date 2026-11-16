"""Pruebas de permisos y operaciones administrativas."""
import pytest

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import Rol, Usuario, PerfilCuidador


@pytest.fixture
def entorno():
    app = create_app("test")
    with app.app_context():
        db.create_all()
        roles = {}
        for nombre in ("ADMIN", "DUENO", "CUIDADOR"):
            rol = Rol(nombre=nombre)
            db.session.add(rol)
            db.session.flush()
            roles[nombre] = rol
        ids = {}
        for nombre, rol in (
            ("admin", "ADMIN"), ("dueno", "DUENO"), ("cuidador", "CUIDADOR")
        ):
            usuario = Usuario(
                nombre=nombre, apellido="Prueba",
                email=f"{nombre}@example.com", telefono="3420000000",
                provincia="Santa Fe", localidad="Santa Fe",
                rol_id=roles[rol].id
            )
            usuario.set_password("ClaveSegura123")
            db.session.add(usuario)
            db.session.flush()
            ids[nombre] = usuario.id
        db.session.add(PerfilCuidador(
            usuario_id=ids["cuidador"], tarifa_diaria=1000, capacidad_maxima=2
        ))
        db.session.commit()
    yield app, ids
    with app.app_context():
        db.session.remove()
        db.drop_all()


def cliente(app, nombre):
    c = app.test_client()
    respuesta = c.post("/api/auth/login", json={
        "email": f"{nombre}@example.com", "password": "ClaveSegura123"
    })
    assert respuesta.status_code == 200
    return c


def test_anonimo_no_puede_acceder(entorno):
    app, ids = entorno
    c = app.test_client()
    assert c.get("/admin/").status_code == 401
    assert c.get("/admin/api/usuarios").status_code == 401


def test_dueno_y_cuidador_no_pueden_acceder(entorno):
    app, ids = entorno
    for nombre in ("dueno", "cuidador"):
        c = cliente(app, nombre)
        assert c.get("/admin/").status_code == 403
        assert c.get("/admin/api/resumen").status_code == 403
        assert c.patch(f"/admin/api/usuarios/{ids['dueno']}/estado",
                       json={"activo": False}).status_code == 403


def test_admin_puede_consultar(entorno):
    app, ids = entorno
    c = cliente(app, "admin")
    assert c.get("/admin/").status_code == 200
    resumen = c.get("/admin/api/resumen")
    assert resumen.status_code == 200
    assert resumen.json["usuarios"] == 3
    for nombre in ("usuarios", "cuidadores", "solicitudes", "incidencias"):
        respuesta = c.get(f"/admin/api/{nombre}")
        assert respuesta.status_code == 200
        assert "items" in respuesta.json


def test_admin_desactiva_y_reactiva(entorno):
    app, ids = entorno
    c = cliente(app, "admin")
    ruta = f"/admin/api/usuarios/{ids['dueno']}/estado"
    assert c.patch(ruta, json={"activo": False}).status_code == 200
    assert cliente_inactivo(app).status_code == 401
    assert c.patch(ruta, json={"activo": True}).status_code == 200


def cliente_inactivo(app):
    return app.test_client().post("/api/auth/login", json={
        "email": "dueno@example.com", "password": "ClaveSegura123"
    })


def test_no_desactivar_administrador(entorno):
    app, ids = entorno
    c = cliente(app, "admin")
    ruta = f"/admin/api/usuarios/{ids['admin']}/estado"
    assert c.patch(ruta, json={"activo": False}).status_code == 403


def test_validaciones(entorno):
    app, ids = entorno
    c = cliente(app, "admin")
    ruta = f"/admin/api/usuarios/{ids['dueno']}/estado"
    assert c.patch(ruta, json={"activo": "no"}).status_code == 400
    assert c.patch("/admin/api/usuarios/99999/estado",
                   json={"activo": False}).status_code == 404
    assert c.get("/admin/api/solicitudes?estado=INVENTADO").status_code == 400


def test_admin_inactivo_no_accede(entorno):
    app, ids = entorno
    c = cliente(app, "admin")
    with app.app_context():
        usuario = db.session.get(Usuario, ids["admin"])
        usuario.activo = False
        db.session.commit()
    assert c.get("/admin/api/resumen").status_code == 403
