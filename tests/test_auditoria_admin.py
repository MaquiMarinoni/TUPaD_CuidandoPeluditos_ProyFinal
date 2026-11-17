"""Auditoría administrativa: SQLite aislado, sin modificar MariaDB."""
from datetime import datetime, timezone
import pytest
from sqlalchemy.exc import IntegrityError
from test_admin import entorno, cliente
from backend.app.extensions import db
from backend.app.models import AuditoriaCuenta, Usuario


def test_cambio_registra_actor_motivo_y_estados(entorno):
    app, ids = entorno
    c = cliente(app, 'admin')
    ruta = f"/admin/api/usuarios/{ids['dueno']}/estado"
    inicio = datetime.now(timezone.utc).replace(tzinfo=None)
    assert c.patch(ruta, json={'activo': False, 'motivo': '  Incumplimiento ficticio  '}).status_code == 200
    assert c.patch(ruta, json={'activo': True, 'motivo': 'Revisión completada'}).status_code == 200
    with app.app_context():
        filas = AuditoriaCuenta.query.order_by(AuditoriaCuenta.id).all()
        assert len(filas) == 2
        assert filas[0].administrador_id == ids['admin']
        assert filas[0].usuario_id == ids['dueno']
        assert (filas[0].activo_anterior, filas[0].activo_nuevo) == (True, False)
        assert (filas[1].activo_anterior, filas[1].activo_nuevo) == (False, True)
        assert filas[0].motivo == 'Incumplimiento ficticio'
        assert filas[0].fecha_cambio >= inicio
        assert db.session.get(Usuario, ids['dueno']).activo is True
    r = c.get(f"/admin/api/usuarios/{ids['dueno']}/auditoria")
    assert r.status_code == 200
    assert r.json['total'] == 2
    assert r.json['items'][0]['motivo'] == 'Revisión completada'
    assert r.json['items'][0]['fecha_cambio'].endswith('Z')


@pytest.mark.parametrize('extra', [{}, {'motivo': ''}, {'motivo': '   '}, {'motivo': None}, {'motivo': 123}, {'motivo': 'x' * 1001}, {'motivo': 'Prueba', 'administrador_id': 999}])
def test_rechaza_motivo_invalido_o_actor_inyectado(entorno, extra):
    app, ids = entorno
    c = cliente(app, 'admin')
    r = c.patch(f"/admin/api/usuarios/{ids['dueno']}/estado", json={'activo': False, **extra})
    assert r.status_code == 400
    with app.app_context():
        assert db.session.get(Usuario, ids['dueno']).activo is True
        assert AuditoriaCuenta.query.count() == 0


def test_repetir_estado_no_agrega_historial(entorno):
    app, ids = entorno
    c = cliente(app, 'admin')
    assert c.patch(f"/admin/api/usuarios/{ids['dueno']}/estado", json={'activo': True, 'motivo': 'Sin cambio'}).status_code == 409
    with app.app_context():
        assert AuditoriaCuenta.query.count() == 0


def test_historial_privado_y_admin_protegido(entorno):
    app, ids = entorno
    ruta = f"/admin/api/usuarios/{ids['dueno']}/auditoria"
    assert app.test_client().get(ruta).status_code == 401
    for nombre in ('dueno', 'cuidador'):
        assert cliente(app, nombre).get(ruta).status_code == 403
    c = cliente(app, 'admin')
    assert c.patch(f"/admin/api/usuarios/{ids['admin']}/estado", json={'activo': False, 'motivo': 'Prueba'}).status_code == 403
    assert c.get('/admin/api/usuarios/99999/auditoria').status_code == 404
    assert c.get(ruta).json['total'] == 0


def test_historial_paginado(entorno):
    app, ids = entorno
    with app.app_context():
        for i in range(21):
            db.session.add(AuditoriaCuenta(usuario_id=ids['dueno'], administrador_id=ids['admin'], activo_anterior=bool(i % 2), activo_nuevo=not bool(i % 2), motivo=f'Prueba {i}'))
        db.session.commit()
    c = cliente(app, 'admin')
    ruta = f"/admin/api/usuarios/{ids['dueno']}/auditoria"
    assert len(c.get(ruta).json['items']) == 20
    segunda = c.get(ruta + '?pagina=2').json
    assert segunda['total'] == 21
    assert len(segunda['items']) == 1


def test_fallo_al_guardar_revierte_estado_y_auditoria(entorno, monkeypatch):
    app, ids = entorno
    c = cliente(app, 'admin')
    def fallo():
        raise IntegrityError('insert', {}, Exception('Fallo simulado'))
    with monkeypatch.context() as m:
        m.setattr(db.session, 'commit', fallo)
        r = c.patch(f"/admin/api/usuarios/{ids['dueno']}/estado", json={'activo': False, 'motivo': 'Prueba de atomicidad'})
        assert r.status_code == 409
    with app.app_context():
        assert db.session.get(Usuario, ids['dueno']).activo is True
        assert AuditoriaCuenta.query.count() == 0
