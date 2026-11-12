"""Ocupacion noche por noche con reservas parcialmente solapadas en MariaDB de pruebas, mediante la API de Flask.

Crea usuarios ficticios propios y cancela sus solicitudes al finalizar.
No modifica las reservas manuales. Requiere DATABASE_URL en la terminal.
"""
import os
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.engine import make_url


def main():
    raw = os.environ.get('DATABASE_URL')
    if not raw:
        raise SystemExit('Configurar DATABASE_URL en esta terminal; no se usara SQLite.')
    url = make_url(raw)
    if not url.drivername.startswith('mysql') or not (url.database or '').endswith('_pruebas'):
        raise SystemExit('Solo se admite MariaDB con una base terminada en _pruebas.')

    from backend.app import create_app
    from backend.app.extensions import db

    app = create_app('dev')
    with app.app_context():
        assert db.engine.dialect.name == 'mysql' and db.engine.url.database == url.database
        print('Motor verificado: MariaDB/MySQL; base:', db.engine.url.database)

    def request(client, method, path, data=None, expected=200):
        token = client.get('/api/auth/csrf-token').get_json()['csrf_token']
        response = client.open(path, method=method, json=data, headers={'X-CSRFToken': token})
        assert response.status_code == expected, (path, response.status_code, response.get_json())
        print(f'OK - {method} {path}: {expected}')
        return response.get_json()

    suffix = uuid4().hex[:12]
    password = 'PruebaCuposParciales2026!'
    owner, caregiver = app.test_client(), app.test_client()
    for client, name, role in [(owner, 'DuenoCuposParciales', 'DUENO'), (caregiver, 'CuidadorCuposParciales', 'CUIDADOR')]:
        email = f'{name.lower()}.{suffix}@example.com'
        request(client, 'POST', '/api/auth/register', dict(nombre=name, apellido='Ficticio', email=email, password=password, telefono='000000', provincia='Santa Fe', localidad='Rosario', rol=role), 201)
        request(client, 'POST', '/api/auth/login', dict(email=email, password=password))
    profile = request(caregiver, 'POST', '/api/cuidadores/mi-perfil', dict(descripcion='Prueba ficticia de ocupacion por noche', capacidad_maxima=2, admite_perros=True, admite_gatos=False, tarifa_diaria='100.00'), 201)['cuidador']['id']
    start = date.today() + timedelta(days=30)
    dates = [(start, start+timedelta(days=2)), (start+timedelta(days=2), start+timedelta(days=4)), (start, start+timedelta(days=4)), (start+timedelta(days=1), start+timedelta(days=3))]
    request(caregiver, 'POST', '/api/disponibilidades', dict(modalidad='ALOJAMIENTO', fecha_desde=start.isoformat(), fecha_hasta=(start+timedelta(days=4)).isoformat()), 201)
    ids = []
    try:
        for letter, (entry, exit_) in zip('ABCD', dates):
            pet = request(owner, 'POST', '/api/mascotas', dict(nombre=f'CuposParciales {letter} ficticio', especie='PERRO', tamano='CHICO'), 201)['mascota']['id']
            s = request(owner, 'POST', '/api/solicitudes', dict(cuidador_id=profile, modalidad='ALOJAMIENTO', fecha_desde=entry.isoformat(), fecha_hasta=exit_.isoformat(), mascotas_ids=[pet], contacto_emergencia='Contacto ficticio cupos parciales', autorizacion_urgencia=False), 201)['solicitud']
            ids.append(s['id'])
            assert Decimal(s['monto_total']) == Decimal((exit_ - entry).days) * Decimal('100.00')
            print(f'Caso {letter}: #{s["id"]}, {entry} al {exit_}, {(exit_ - entry).days} noches')
        request(caregiver, 'POST', f'/api/solicitudes/{ids[0]}/aceptar')
        request(caregiver, 'POST', f'/api/solicitudes/{ids[1]}/aceptar')
        print('OK - A y B aceptadas: no coinciden entre si')
        request(caregiver, 'POST', f'/api/solicitudes/{ids[2]}/aceptar')
        print('OK - C aceptada: coincide con A y con B, pero solo ocupa dos plazas por noche')
        request(caregiver, 'POST', f'/api/solicitudes/{ids[3]}/aceptar', expected=409)
        states = [request(owner, 'GET', f'/api/solicitudes/{sid}')['solicitud']['estado'] for sid in ids]
        assert states == ['ACEPTADA', 'ACEPTADA', 'ACEPTADA', 'PENDIENTE'], states
        print('OK - Estados persistidos:', states)
        print('OK - Sobrecupo real de D bloqueado sin cambiarlo a RECHAZADA')
    finally:
        for sid in ids:
            request(owner, 'POST', f'/api/solicitudes/{sid}/cancelar')
        print('Solicitudes propias canceladas; usuarios, perfil, disponibilidad y mascotas ficticios permanecen.')
    print('TODAS LAS PRUEBAS DE OCUPACION POR NOCHE PASARON')


if __name__ == '__main__':
    main()
