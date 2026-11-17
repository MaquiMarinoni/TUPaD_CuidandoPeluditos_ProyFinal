"""Disponibilidades útiles para visitas nuevas; SQLite aislado."""
from datetime import date, timedelta, time
from decimal import Decimal
import pytest
from test_finalizacion import servicio_historico
from backend.app.extensions import db
from backend.app.models import Solicitud, Disponibilidad


@pytest.fixture
def agenda(servicio_historico):
    app, sid = servicio_historico
    with app.app_context():
        perfil = db.session.get(Solicitud, sid).cuidador_perfil
        perfil.tarifa_visita = Decimal('80')
        perfil_id = perfil.id
        db.session.commit()
    cliente = app.test_client()
    assert cliente.post('/api/auth/login', json=dict(email='cuidador@example.com', password='PruebaLocal2026!')).status_code == 200
    return app, cliente, perfil_id


@pytest.mark.parametrize('fin,codigo', [('15:05',400), ('15:59',400), ('16:00',201), ('17:00',201)])
def test_publicar_exige_hora_completa(agenda, fin, codigo):
    app, cliente, perfil_id = agenda
    dia = (date.today()+timedelta(days=2)).isoformat()
    r = cliente.post('/api/disponibilidades', json=dict(modalidad='VISITA', fecha_desde=dia, fecha_hasta=dia, hora_desde='15:00', hora_hasta=fin))
    assert r.status_code == codigo, r.json
    with app.app_context():
        assert Disponibilidad.query.filter_by(cuidador_id=perfil_id).count() == (1 if codigo == 201 else 0)


def test_publico_oculta_cortas_y_vencidas_sin_borrar_agenda(agenda):
    app, cliente, perfil_id = agenda
    hoy = date.today()
    with app.app_context():
        registros = []
        for desde,hasta,inicio,fin in [
            (hoy,hoy,time(9),time(9,5)),
            (hoy,hoy,time(10),time(11)),
            (hoy-timedelta(days=2),hoy-timedelta(days=1),time(12),time(14)),
            (hoy-timedelta(days=1),hoy+timedelta(days=2),time(15),time(17)),
        ]:
            registros.append(Disponibilidad(cuidador_id=perfil_id, modalidad='VISITA', fecha_desde=desde,fecha_hasta=hasta,hora_desde=inicio,hora_hasta=fin,activo=True))
        alojamiento = Disponibilidad(cuidador_id=perfil_id, modalidad='ALOJAMIENTO',fecha_desde=hoy,fecha_hasta=hoy+timedelta(days=2),activo=True)
        db.session.add_all(registros+[alojamiento])
        db.session.commit()
        todos = {d.id for d in registros+[alojamiento]}
        esperados = {registros[1].id,registros[3].id,alojamiento.id}
    publico = app.test_client().get(f'/api/cuidadores/{perfil_id}/disponibilidades')
    assert publico.status_code == 200
    assert {d['id'] for d in publico.json['disponibilidades']} == esperados
    propia = cliente.get('/api/disponibilidades')
    assert {d['id'] for d in propia.json['disponibilidades']} == todos
    with app.app_context():
        assert Disponibilidad.query.count() == len(todos)


def test_editar_franja_antigua_permite_corregirla(agenda):
    app, cliente, perfil_id = agenda
    dia = date.today()+timedelta(days=3)
    with app.app_context():
        d = Disponibilidad(cuidador_id=perfil_id,modalidad='VISITA',fecha_desde=dia,fecha_hasta=dia,hora_desde=time(15),hora_hasta=time(15,5),activo=True)
        db.session.add(d)
        db.session.commit()
        did = d.id
    datos = dict(modalidad='VISITA',fecha_desde=dia.isoformat(),fecha_hasta=dia.isoformat(),hora_desde='15:00',hora_hasta='15:05')
    assert cliente.put(f'/api/disponibilidades/{did}',json=datos).status_code == 400
    with app.app_context():
        assert db.session.get(Disponibilidad,did).hora_hasta == time(15,5)
    datos['hora_hasta']='16:00'
    assert cliente.put(f'/api/disponibilidades/{did}',json=datos).status_code == 200
    publico = app.test_client().get(f'/api/cuidadores/{perfil_id}/disponibilidades')
    assert {d['id'] for d in publico.json['disponibilidades']} == {did}
