"""Contactos de coordinación: pruebas aisladas de permisos e historial."""
import pytest
from test_privacidad_solicitudes import escenario, ingresar
from backend.app.extensions import db
from backend.app.models import Solicitud, Disponibilidad, Usuario


@pytest.mark.parametrize('modalidad', ['ALOJAMIENTO', 'VISITA'])
@pytest.mark.parametrize('actor', ['Dueno', 'Cuidador'])
@pytest.mark.parametrize('estado, visible', [('PENDIENTE', False), ('ACEPTADA', True), ('FINALIZADA', True), ('CANCELADA', False), ('RECHAZADA', False)])
def test_contactos_solo_participantes_y_estados_acordados(escenario, modalidad, actor, estado, visible):
    app, ids=escenario
    with app.app_context():
        s=db.session.get(Solicitud,ids[modalidad])
        s.estado=estado
        db.session.commit()
    c=app.test_client(); ingresar(c,actor)
    r=c.get(f"/api/solicitudes/{ids[modalidad]}")
    assert r.status_code==200
    contactos=r.json['solicitud']['contactos']
    assert bool(contactos)==visible
    if visible:
        assert contactos['dueno']['email']=='dueno@example.com'
        assert contactos['cuidador']['email']=='cuidador@example.com'
        assert contactos['dueno']['telefono']=='1234567'
        assert all('password' not in str(datos) for datos in contactos.values())


def test_tercero_y_anonimo_no_reciben_contactos(escenario):
    app,ids=escenario
    with app.app_context():
        db.session.get(Solicitud,ids['ALOJAMIENTO']).estado='ACEPTADA'
        db.session.commit()
    c=app.test_client()
    assert c.get(f"/api/solicitudes/{ids['ALOJAMIENTO']}").status_code==401
    ingresar(c,'Ajeno')
    assert c.get(f"/api/solicitudes/{ids['ALOJAMIENTO']}").status_code==404


def test_direccion_de_perfil_privada_y_snapshot_al_aceptar(escenario):
    app,ids=escenario
    with app.app_context():
        s=db.session.get(Solicitud,ids['ALOJAMIENTO'])
        s.direccion_servicio=None
        perfil=s.cuidador_perfil
        perfil_id=perfil.id
        db.session.add(Disponibilidad(cuidador_id=perfil.id, modalidad='ALOJAMIENTO',fecha_desde=s.fecha_desde,fecha_hasta=s.fecha_hasta,activo=True))
        db.session.commit()
    c=app.test_client();ingresar(c,'Cuidador')
    r=c.put('/api/cuidadores/mi-perfil',json={'direccion_alojamiento':'Calle ficticia 123'})
    assert r.status_code==200
    assert r.json['cuidador']['direccion_alojamiento']=='Calle ficticia 123'
    assert c.get('/api/cuidadores/mi-perfil').json['cuidador']['direccion_alojamiento']=='Calle ficticia 123'
    for ruta in ('/api/cuidadores',f'/api/cuidadores/{perfil_id}'):
        publico=app.test_client().get(ruta)
        assert 'Calle ficticia 123' not in publico.get_data(as_text=True)
        assert 'direccion_alojamiento' not in publico.get_data(as_text=True)
    assert c.post(f"/api/solicitudes/{ids['ALOJAMIENTO']}/aceptar").status_code==200
    assert c.put('/api/cuidadores/mi-perfil',json={'direccion_alojamiento':'Otra dirección 456'}).status_code==200
    dueno=app.test_client();ingresar(dueno,'Dueno')
    detalle=dueno.get(f"/api/solicitudes/{ids['ALOJAMIENTO']}").json['solicitud']
    assert detalle['direccion_servicio']=='Calle ficticia 123'
    assert detalle['contactos']['cuidador']['email']=='cuidador@example.com'
    assert dueno.get('/api/cuidadores/mi-perfil').status_code==403


@pytest.mark.parametrize('valor',[123,'x'*121])
def test_valida_direccion_sin_cambiar_otros_datos(escenario,valor):
    app,_=escenario
    c=app.test_client();ingresar(c,'Cuidador')
    assert c.put('/api/cuidadores/mi-perfil',json={'direccion_alojamiento':valor}).status_code==400
