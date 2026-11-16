"""Resumen de cupos: pruebas aisladas, sin tocar MariaDB."""
from datetime import date, timedelta
from types import SimpleNamespace as N
from test_finalizacion import servicio_historico
from backend.app.cupos_publicos import tramos_cupo
from backend.app.extensions import db
from backend.app.models import Solicitud, Disponibilidad

D = date(2030, 1, 1)
def reserva(desde, hasta, cantidad=1, estado='ACEPTADA'):
    return N(fecha_desde=D+timedelta(days=desde), fecha_hasta=D+timedelta(days=hasta), total_mascotas=cantidad, estado=estado, modalidad='ALOJAMIENTO')
def resumen(reservas, capacidad=3):
    return tramos_cupo(N(fecha_desde=D, fecha_hasta=D+timedelta(days=5)), capacidad, reservas, hoy=D)

def test_reserva_parcial_deja_libres_las_otras_noches():
    r = resumen([reserva(1, 4)])
    assert [(t['fecha_desde'], t['fecha_hasta'], t['plazas_libres']) for t in r] == [('2030-01-01','2030-01-02',3), ('2030-01-02','2030-01-05',2), ('2030-01-05','2030-01-06',3)]

def test_recambio_mismo_dia_no_suma_dos_reservas():
    assert resumen([reserva(0,2), reserva(2,5)], 1) == [dict(fecha_desde='2030-01-01', fecha_hasta='2030-01-06', plazas_libres=0)]

def test_pendientes_y_canceladas_no_ocupan():
    assert resumen([reserva(0,5,estado='PENDIENTE'), reserva(0,5,estado='CANCELADA')])[0]['plazas_libres'] == 3

def test_solapamiento_parcial_y_liberacion():
    a,b = reserva(0,3), reserva(2,5)
    assert [t['plazas_libres'] for t in resumen([a,b],2)] == [1,0,1]
    a.estado='CANCELADA'
    assert [t['plazas_libres'] for t in resumen([a,b],2)] == [2,1]

def test_recorta_noches_pasadas():
    d=N(fecha_desde=D, fecha_hasta=D+timedelta(days=5))
    assert tramos_cupo(d,3,[],hoy=D+timedelta(days=2))[0]['fecha_desde']=='2030-01-03'
    assert tramos_cupo(d,3,[],hoy=D+timedelta(days=5)) == []

def test_endpoint_publico_sin_datos_personales_y_actualiza_al_cancelar(servicio_historico):
    app,sid=servicio_historico
    inicio=date.today()+timedelta(days=2)
    with app.app_context():
        s=db.session.get(Solicitud,sid)
        s.fecha_desde=inicio+timedelta(days=1)
        s.fecha_hasta=inicio+timedelta(days=3)
        perfil_id=s.cuidador_id
        db.session.add(Disponibilidad(cuidador_id=perfil_id, modalidad='ALOJAMIENTO', fecha_desde=inicio,fecha_hasta=inicio+timedelta(days=5),activo=True))
        db.session.commit()
    cliente=app.test_client()
    r=cliente.get(f'/api/cuidadores/{perfil_id}/disponibilidades')
    assert r.status_code==200
    tramos=r.json['disponibilidades'][0]['tramos_cupo']
    assert [t['plazas_libres'] for t in tramos]==[1,0,1]
    assert all(set(t)=={'fecha_desde','fecha_hasta','plazas_libres'} for t in tramos)
    with app.app_context():
        db.session.get(Solicitud,sid).estado='CANCELADA'
        db.session.commit()
    r=cliente.get(f'/api/cuidadores/{perfil_id}/disponibilidades')
    assert len(r.json['disponibilidades'][0]['tramos_cupo'])==1
    assert r.json['disponibilidades'][0]['tramos_cupo'][0]['plazas_libres']==1
