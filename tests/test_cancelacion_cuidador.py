"""Reglas de cancelacion con SQLite aislado; no modifica MariaDB."""
from datetime import date, timedelta, time

import pytest
from test_finalizacion import servicio_historico
from backend.app.extensions import db
from backend.app.models import Solicitud, HistorialEstado


@pytest.mark.parametrize('modalidad', ['ALOJAMIENTO', 'VISITA'])
@pytest.mark.parametrize('actor', ['dueno', 'cuidador'])
def test_cancelar_aceptada_futura_registra_actor(servicio_historico, modalidad, actor):
    app, sid = servicio_historico
    with app.app_context():
        s = db.session.get(Solicitud, sid)
        s.modalidad = modalidad
        s.fecha_desde = date.today() + timedelta(days=2)
        s.fecha_hasta = s.fecha_desde if modalidad == 'VISITA' else s.fecha_desde + timedelta(days=2)
        if modalidad == 'VISITA':
            s.hora_desde, s.hora_hasta = time(10), time(11)
        db.session.commit()
    client = app.test_client()
    assert client.post('/api/auth/login', json={'email': f'{actor}@example.com', 'password': 'PruebaLocal2026!'}).status_code == 200
    response = client.post(f'/api/solicitudes/{sid}/cancelar')
    assert response.status_code == 200
    assert response.json['solicitud']['estado'] == 'CANCELADA'
    with app.app_context():
        s = db.session.get(Solicitud, sid)
        assert s.estado == 'CANCELADA'
        h = HistorialEstado.query.filter_by(solicitud_id=sid, estado_nuevo='CANCELADA').one()
        expected = s.dueno_id if actor == 'dueno' else s.cuidador_perfil.usuario_id
        assert h.usuario_id == expected
        assert h.estado_anterior == 'ACEPTADA'
    assert client.post(f'/api/solicitudes/{sid}/cancelar').status_code == 409


@pytest.mark.parametrize('modalidad', ['ALOJAMIENTO', 'VISITA'])
def test_cuidador_no_cancela_servicio_iniciado(servicio_historico, modalidad):
    app, sid = servicio_historico
    with app.app_context():
        s = db.session.get(Solicitud, sid)
        s.modalidad = modalidad
        s.fecha_desde = date.today() - timedelta(days=1)
        s.fecha_hasta = s.fecha_desde if modalidad == 'VISITA' else date.today() + timedelta(days=1)
        if modalidad == 'VISITA':
            s.hora_desde, s.hora_hasta = time(10), time(11)
        db.session.commit()
    client = app.test_client()
    client.post('/api/auth/login', json={'email': 'cuidador@example.com', 'password': 'PruebaLocal2026!'})
    assert client.post(f'/api/solicitudes/{sid}/cancelar').status_code == 409
    with app.app_context():
        assert db.session.get(Solicitud, sid).estado == 'ACEPTADA'
        assert HistorialEstado.query.filter_by(solicitud_id=sid, estado_nuevo='CANCELADA').count() == 0


def test_cuidador_rechaza_pendiente_no_la_cancela(servicio_historico):
    app, sid = servicio_historico
    with app.app_context():
        s = db.session.get(Solicitud, sid)
        s.estado = 'PENDIENTE'
        s.fecha_desde = date.today() + timedelta(days=2)
        s.fecha_hasta = s.fecha_desde + timedelta(days=1)
        db.session.commit()
    client = app.test_client()
    client.post('/api/auth/login', json={'email': 'cuidador@example.com', 'password': 'PruebaLocal2026!'})
    assert client.post(f'/api/solicitudes/{sid}/cancelar').status_code == 409
    assert client.post(f'/api/solicitudes/{sid}/rechazar').status_code == 200
