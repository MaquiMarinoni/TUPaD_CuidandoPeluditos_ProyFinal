
"""Pruebas de permisos y operaciones administrativas."""

from datetime import date

import pytest

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import (
    Rol,
    Usuario,
    PerfilCuidador,
    Mascota,
    Solicitud,
    SolicitudMascota,
    Incidencia,
    HistorialEstado,
)


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
            ("admin", "ADMIN"),
            ("dueno", "DUENO"),
            ("cuidador", "CUIDADOR"),
        ):
            usuario = Usuario(
                nombre=nombre,
                apellido="Prueba",
                email=f"{nombre}@example.com",
                telefono="3420000000",
                provincia="Santa Fe",
                localidad="Santa Fe",
                rol_id=roles[rol].id,
            )
            usuario.set_password("ClaveSegura123")
            db.session.add(usuario)
            db.session.flush()
            ids[nombre] = usuario.id

        db.session.add(
            PerfilCuidador(
                usuario_id=ids["cuidador"],
                tarifa_diaria=1000,
                capacidad_maxima=2,
            )
        )

        db.session.commit()

    yield app, ids

    with app.app_context():
        db.session.remove()
        db.drop_all()


def cliente(app, nombre):
    c = app.test_client()

    respuesta = c.post(
        "/api/auth/login",
        json={
            "email": f"{nombre}@example.com",
            "password": "ClaveSegura123",
        },
    )

    assert respuesta.status_code == 200
    return c


def cliente_inactivo(app):
    return app.test_client().post(
        "/api/auth/login",
        json={
            "email": "dueno@example.com",
            "password": "ClaveSegura123",
        },
    )


# ---------------------------------------------------------
# Pruebas originales
# ---------------------------------------------------------

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

        assert c.patch(
            f"/admin/api/usuarios/{ids['dueno']}/estado",
            json={"activo": False, "motivo": "Prueba administrativa"},
        ).status_code == 403


def test_admin_puede_consultar(entorno):
    app, ids = entorno
    c = cliente(app, "admin")

    assert c.get("/admin/").status_code == 200

    resumen = c.get("/admin/api/resumen")

    assert resumen.status_code == 200
    assert resumen.json["usuarios"] == 3

    for nombre in (
        "usuarios",
        "cuidadores",
        "solicitudes",
        "incidencias",
    ):
        respuesta = c.get(f"/admin/api/{nombre}")

        assert respuesta.status_code == 200
        assert "items" in respuesta.json


def test_admin_desactiva_y_reactiva(entorno):
    app, ids = entorno
    c = cliente(app, "admin")

    ruta = f"/admin/api/usuarios/{ids['dueno']}/estado"

    assert c.patch(
        ruta,
        json={"activo": False, "motivo": "Prueba administrativa"},
    ).status_code == 200

    assert cliente_inactivo(app).status_code == 401

    assert c.patch(
        ruta,
        json={"activo": True, "motivo": "Reactivación de prueba"},
    ).status_code == 200


def test_no_desactivar_administrador(entorno):
    app, ids = entorno
    c = cliente(app, "admin")

    ruta = f"/admin/api/usuarios/{ids['admin']}/estado"

    assert c.patch(
        ruta,
        json={"activo": False, "motivo": "Prueba administrativa"},
    ).status_code == 403


def test_validaciones(entorno):
    app, ids = entorno
    c = cliente(app, "admin")

    ruta = f"/admin/api/usuarios/{ids['dueno']}/estado"

    assert c.patch(
        ruta,
        json={"activo": "no"},
    ).status_code == 400

    assert c.patch(
        "/admin/api/usuarios/99999/estado",
        json={"activo": False, "motivo": "Prueba administrativa"},
    ).status_code == 404

    assert c.get(
        "/admin/api/solicitudes?estado=INVENTADO"
    ).status_code == 400


def test_admin_inactivo_no_accede(entorno):
    app, ids = entorno
    c = cliente(app, "admin")

    with app.app_context():
        usuario = db.session.get(Usuario, ids["admin"])
        usuario.activo = False
        db.session.commit()

    assert c.get("/admin/api/resumen").status_code == 403


# ---------------------------------------------------------
# Consultas detalladas
# ---------------------------------------------------------

def test_admin_consulta_detalle_dueno(entorno):
    app, ids = entorno
    c = cliente(app, "admin")

    respuesta = c.get(f"/admin/api/duenos/{ids['dueno']}")

    assert respuesta.status_code == 200
    assert respuesta.json["id"] == ids["dueno"]
    assert respuesta.json["email"] == "dueno@example.com"
    assert respuesta.json["activo"] is True
    assert respuesta.json["mascotas"] == []


def test_admin_consulta_historial_dueno(entorno):
    app, ids = entorno
    c = cliente(app, "admin")

    respuesta = c.get(
        f"/admin/api/duenos/{ids['dueno']}/solicitudes"
    )

    assert respuesta.status_code == 200
    assert respuesta.json["items"] == []
    assert respuesta.json["total"] == 0


def test_admin_consulta_detalle_cuidador(entorno):
    app, ids = entorno
    c = cliente(app, "admin")

    with app.app_context():
        perfil = PerfilCuidador.query.filter_by(
            usuario_id=ids["cuidador"]
        ).first()
        perfil_id = perfil.id

    respuesta = c.get(f"/admin/api/cuidadores/{perfil_id}")

    assert respuesta.status_code == 200
    assert respuesta.json["usuario_id"] == ids["cuidador"]
    assert respuesta.json["email"] == "cuidador@example.com"
    assert respuesta.json["capacidad_maxima"] == 2


def test_admin_consulta_servicios_cuidador(entorno):
    app, ids = entorno
    c = cliente(app, "admin")

    with app.app_context():
        perfil = PerfilCuidador.query.filter_by(
            usuario_id=ids["cuidador"]
        ).first()
        perfil_id = perfil.id

    respuesta = c.get(
        f"/admin/api/cuidadores/{perfil_id}/servicios"
    )

    assert respuesta.status_code == 200
    assert respuesta.json["items"] == []
    assert respuesta.json["total"] == 0


@pytest.mark.parametrize("ruta", [
    "/admin/api/duenos/99999",
    "/admin/api/duenos/99999/solicitudes",
    "/admin/api/cuidadores/99999",
    "/admin/api/cuidadores/99999/servicios",
])
def test_admin_consultas_registros_inexistentes(entorno, ruta):
    app, ids = entorno
    c = cliente(app, "admin")

    assert c.get(ruta).status_code == 404


def test_dueno_no_puede_consultar_detalles_admin(entorno):
    app, ids = entorno
    c = cliente(app, "dueno")

    rutas = [
        f"/admin/api/duenos/{ids['dueno']}",
        f"/admin/api/duenos/{ids['dueno']}/solicitudes",
    ]

    for ruta in rutas:
        assert c.get(ruta).status_code == 403


def test_cuidador_no_puede_consultar_detalles_admin(entorno):
    app, ids = entorno
    c = cliente(app, "cuidador")

    with app.app_context():
        perfil = PerfilCuidador.query.filter_by(
            usuario_id=ids["cuidador"]
        ).first()
        perfil_id = perfil.id

    rutas = [
        f"/admin/api/cuidadores/{perfil_id}",
        f"/admin/api/cuidadores/{perfil_id}/servicios",
    ]

    for ruta in rutas:
        assert c.get(ruta).status_code == 403


# ---------------------------------------------------------
# Prueba integral con registros relacionados
# ---------------------------------------------------------

def test_admin_consulta_datos_relacionados(entorno):
    app, ids = entorno

    with app.app_context():
        perfil = PerfilCuidador.query.filter_by(
            usuario_id=ids["cuidador"]
        ).first()

        perfil_id = perfil.id

        mascota = Mascota(
            dueno_id=ids["dueno"],
            nombre="Luna",
            especie="PERRO",
            raza="Mestiza",
            tamano="MEDIANO",
            cuidados_especiales="Necesita medicacion",
            contacto_veterinario="Veterinaria de prueba",
        )
        db.session.add(mascota)
        db.session.flush()

        solicitud = Solicitud(
            dueno_id=ids["dueno"],
            cuidador_id=perfil_id,
            modalidad="ALOJAMIENTO",
            fecha_desde=date(2026, 11, 20),
            fecha_hasta=date(2026, 11, 22),
            estado="ACEPTADA",
            total_mascotas=1,
            monto_total=3000,
            contacto_emergencia="Contacto de prueba",
        )
        db.session.add(solicitud)
        db.session.flush()

        solicitud_id = solicitud.id

        db.session.add(
            SolicitudMascota(
                solicitud_id=solicitud_id,
                mascota_id=mascota.id,
                nombre_snapshot="Luna",
                especie_snapshot="PERRO",
                cuidados_snapshot="Necesita medicacion",
            )
        )

        db.session.add(
            HistorialEstado(
                solicitud_id=solicitud_id,
                usuario_id=ids["cuidador"],
                estado_anterior="PENDIENTE",
                estado_nuevo="ACEPTADA",
                motivo="Solicitud aceptada",
            )
        )

        db.session.add(
            Incidencia(
                solicitud_id=solicitud_id,
                reportado_por_id=ids["cuidador"],
                tipo="SALUD",
                descripcion="Observacion veterinaria de prueba",
                medidas_tomadas="Se aviso al dueño",
                comentario_cierre="Situacion resuelta",
                estado="RESUELTA",
            )
        )

        db.session.commit()

    c = cliente(app, "admin")

    # Datos del dueño y sus mascotas
    respuesta_dueno = c.get(
        f"/admin/api/duenos/{ids['dueno']}"
    )

    assert respuesta_dueno.status_code == 200
    assert len(respuesta_dueno.json["mascotas"]) == 1
    assert respuesta_dueno.json["mascotas"][0]["nombre"] == "Luna"
    assert (
        respuesta_dueno.json["mascotas"][0]["cuidados_especiales"]
        == "Necesita medicacion"
    )

    # Historial de solicitudes del dueño
    respuesta_solicitudes = c.get(
        f"/admin/api/duenos/{ids['dueno']}/solicitudes"
    )

    assert respuesta_solicitudes.status_code == 200
    assert respuesta_solicitudes.json["total"] == 1

    solicitud_json = respuesta_solicitudes.json["items"][0]

    assert solicitud_json["id"] == solicitud_id
    assert solicitud_json["estado"] == "ACEPTADA"
    assert solicitud_json["modalidad"] == "ALOJAMIENTO"
    assert solicitud_json["cuidador"]["id"] == perfil_id
    assert solicitud_json["mascotas"][0]["nombre"] == "Luna"

    assert len(solicitud_json["historial_estados"]) == 1
    assert (
        solicitud_json["historial_estados"][0]["estado_nuevo"]
        == "ACEPTADA"
    )

    # Historial de servicios del cuidador
    respuesta_servicios = c.get(
        f"/admin/api/cuidadores/{perfil_id}/servicios"
    )

    assert respuesta_servicios.status_code == 200
    assert respuesta_servicios.json["total"] == 1

    servicio_json = respuesta_servicios.json["items"][0]

    assert servicio_json["id"] == solicitud_id
    assert servicio_json["estado"] == "ACEPTADA"
    assert servicio_json["dueno"]["id"] == ids["dueno"]

    assert len(servicio_json["historial_estados"]) == 1

    # Incidencias y detalle completo
    assert len(servicio_json["incidencias"]) == 1

    incidencia_json = servicio_json["incidencias"][0]

    assert incidencia_json["tipo"] == "SALUD"
    assert incidencia_json["estado"] == "RESUELTA"
    assert (
        incidencia_json["medidas_tomadas"]
        == "Se aviso al dueño"
    )
    assert (
        incidencia_json["comentario_cierre"]
        == "Situacion resuelta"
    )
