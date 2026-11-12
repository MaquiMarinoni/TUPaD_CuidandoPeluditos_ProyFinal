"""Privacidad de datos personales en solicitudes de alojamiento y visitas."""
from datetime import date, timedelta, time
import pytest

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import Rol, Usuario, PerfilCuidador, Mascota, Solicitud, SolicitudMascota


@pytest.fixture
def escenario():
    app = create_app("test")
    with app.app_context():
        db.create_all()
        dueno_rol = Rol(nombre="DUENO")
        cuidador_rol = Rol(nombre="CUIDADOR")
        db.session.add_all([dueno_rol, cuidador_rol])
        db.session.flush()
        usuarios = []
        for nombre, rol in (("Dueno", dueno_rol), ("Cuidador", cuidador_rol), ("Ajeno", dueno_rol)):
            u = Usuario(nombre=nombre, apellido="Prueba", email=f"{nombre.lower()}@example.com", telefono="1234567", provincia="Santa Fe", localidad="Santa Fe", rol_id=rol.id)
            u.set_password("Prueba2026!")
            db.session.add(u)
            usuarios.append(u)
        db.session.flush()
        dueno, cuidador, ajeno = usuarios
        perfil = PerfilCuidador(usuario_id=cuidador.id, capacidad_maxima=2, tarifa_diaria=100, tarifa_visita=80, admite_perros=True, admite_gatos=True)
        mascota = Mascota(dueno_id=dueno.id, nombre="Luna", especie="PERRO", tamano="CHICO", cuidados_especiales="Necesita medicacion", contacto_veterinario="Veterinaria de prueba")
        db.session.add_all([perfil, mascota])
        db.session.flush()
        ids = {}
        for modalidad in ("ALOJAMIENTO", "VISITA"):
            s = Solicitud(dueno_id=dueno.id, cuidador_id=perfil.id, modalidad=modalidad, fecha_desde=date.today() + timedelta(days=2), fecha_hasta=date.today() + timedelta(days=3 if modalidad == "ALOJAMIENTO" else 2), hora_desde=time(10, 0) if modalidad == "VISITA" else None, hora_hasta=time(11, 0) if modalidad == "VISITA" else None, estado="PENDIENTE", total_mascotas=1, monto_total=100, contacto_emergencia="Contacto privado", veterinario_emergencia="Veterinario privado", autorizacion_urgencia=True, limite_gastos_urgencia=500, direccion_servicio="Direccion privada")
            s.mascotas_asociadas.append(SolicitudMascota(mascota_id=mascota.id, nombre_snapshot="Luna", especie_snapshot="PERRO", cuidados_snapshot="Medicacion privada", veterinario_snapshot="Veterinaria privada"))
            db.session.add(s)
            db.session.flush()
            ids[modalidad] = s.id
        db.session.commit()
    yield app, ids
    with app.app_context():
        db.session.remove()
        db.drop_all()


def ingresar(cliente, nombre):
    r = cliente.post("/api/auth/login", json={"email": f"{nombre.lower()}@example.com", "password": "Prueba2026!"})
    assert r.status_code == 200


@pytest.mark.parametrize("modalidad", ["ALOJAMIENTO", "VISITA"])
def test_cuidador_pendiente_no_ve_privados_y_dueno_si(escenario, modalidad):
    app, ids = escenario
    c = app.test_client()
    url = f"/api/solicitudes/{ids[modalidad]}"
    ingresar(c, "Cuidador")
    r = c.get(url)
    assert r.status_code == 200
    s = r.json["solicitud"]
    for campo in ("direccion_servicio", "contacto_emergencia", "veterinario_emergencia", "limite_gastos_urgencia"):
        assert s[campo] is None, campo
    assert s["mascotas"][0]["cuidados_especiales"] is None
    assert s["mascotas"][0]["contacto_veterinario"] is None
    c.post("/api/auth/logout")
    ingresar(c, "Dueno")
    r = c.get(url)
    assert r.status_code == 200
    s = r.json["solicitud"]
    assert s["direccion_servicio"] == "Direccion privada"
    assert s["contacto_emergencia"] == "Contacto privado"
    assert s["mascotas"][0]["cuidados_especiales"] == "Medicacion privada"


@pytest.mark.parametrize("modalidad", ["ALOJAMIENTO", "VISITA"])
def test_cuidador_aceptada_ve_privados(escenario, modalidad):
    app, ids = escenario
    with app.app_context():
        s = db.session.get(Solicitud, ids[modalidad])
        s.estado = "ACEPTADA"
        db.session.commit()
    c = app.test_client()
    ingresar(c, "Cuidador")
    r = c.get(f"/api/solicitudes/{ids[modalidad]}")
    assert r.status_code == 200
    s = r.json["solicitud"]
    assert s["direccion_servicio"] == "Direccion privada"
    assert s["contacto_emergencia"] == "Contacto privado"
    assert s["mascotas"][0]["contacto_veterinario"] == "Veterinaria privada"


def test_otro_dueno_no_ve_solicitud(escenario):
    app, ids = escenario
    c = app.test_client()
    ingresar(c, "Ajeno")
    assert c.get(f"/api/solicitudes/{ids['VISITA']}").status_code == 404