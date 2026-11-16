"""Reglas nuevas de visitas con SQLite aislado; no modifica MariaDB."""
from datetime import date, timedelta, time
from decimal import Decimal
import pytest
from test_finalizacion import servicio_historico
from backend.app.extensions import db
from backend.app.models import Solicitud, Mascota, Disponibilidad


@pytest.fixture
def visita(servicio_historico):
    app, sid = servicio_historico
    dia = date.today() + timedelta(days=30)
    with app.app_context():
        historica = db.session.get(Solicitud, sid)
        perfil = historica.cuidador_perfil
        perfil.tarifa_visita = Decimal('80.00')
        db.session.add(Disponibilidad(cuidador_id=perfil.id, modalidad='VISITA', fecha_desde=dia, fecha_hasta=dia, hora_desde=time(9), hora_hasta=time(15), activo=True))
        mascotas = [Mascota(dueno_id=historica.dueno_id, nombre=f'Prueba {i}', especie='PERRO', tamano='CHICO') for i in range(4)]
        db.session.add_all(mascotas)
        db.session.commit()
        ids = [m.id for m in mascotas]
        datos = dict(cuidador_id=perfil.id, fecha=dia.isoformat(), hora_desde='10:00', mascotas_ids=ids[:1], direccion_servicio='Domicilio ficticio', contacto_emergencia='Contacto ficticio', autorizacion_urgencia=False)
    cliente = app.test_client()
    assert cliente.post('/api/auth/login', json=dict(email='dueno@example.com', password='PruebaLocal2026!')).status_code == 200
    return app, cliente, datos, ids, sid


@pytest.mark.parametrize('cantidad', [1, 2, 3])
def test_calcula_fin_y_precio_por_mascota(visita, cantidad):
    app, cliente, datos, ids, _ = visita
    datos['mascotas_ids'] = ids[:cantidad]
    r = cliente.post('/api/visitas', json=datos)
    assert r.status_code == 201, r.json
    s = r.json['solicitud']
    assert s['hora_hasta'].startswith('11:00')
    assert Decimal(str(s['monto_total'])) == Decimal(80 * cantidad)
    with app.app_context():
        guardada = db.session.get(Solicitud, s['id'])
        assert guardada.hora_hasta == time(11)
        assert guardada.monto_total == Decimal(80 * cantidad)


@pytest.mark.parametrize('fin', ['10:15', '12:00', '09:00'])
def test_rechaza_duracion_alterada(visita, fin):
    _, cliente, datos, _, _ = visita
    datos['hora_hasta'] = fin
    assert cliente.post('/api/visitas', json=datos).status_code == 400


def test_rechaza_cuarta_mascota(visita):
    _, cliente, datos, ids, _ = visita
    datos['mascotas_ids'] = ids
    assert cliente.post('/api/visitas', json=datos).status_code == 400


@pytest.mark.parametrize('inicio, esperado', [('14:30', 409), ('23:00', 400)])
def test_exige_hora_completa_en_disponibilidad(visita, inicio, esperado):
    _, cliente, datos, _, _ = visita
    datos['hora_desde'] = inicio
    assert cliente.post('/api/visitas', json=datos).status_code == esperado


def test_no_modifica_visita_anterior(visita):
    app, cliente, datos, _, sid = visita
    with app.app_context():
        s = db.session.get(Solicitud, sid)
        s.modalidad = 'VISITA'
        s.fecha_hasta = s.fecha_desde
        s.hora_desde, s.hora_hasta = time(10), time(11, 30)
        s.monto_total = Decimal('50.00')
        db.session.commit()
    assert cliente.post('/api/visitas', json=datos).status_code == 201
    detalle = cliente.get(f'/api/solicitudes/{sid}').json['solicitud']
    assert detalle['hora_hasta'].startswith('11:30')
    assert Decimal(str(detalle['monto_total'])) == Decimal('50.00')
