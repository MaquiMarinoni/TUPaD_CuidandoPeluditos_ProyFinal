"""Comprueba finalización real HTTP contra MariaDB de pruebas.

Requisitos: DATABASE_URL debe apuntar a MariaDB, a una base cuyo nombre
termine en _pruebas. El script crea entidades ficticias, comprueba que el
servicio se finaliza, verifica historial y repetición, y las elimina.

Ejecutar desde la raíz: python scripts/prueba_finalizacion_mariadb.py
"""
import os
import sys
from datetime import date, timedelta
from uuid import uuid4

from sqlalchemy.engine import make_url


def main():
    url_raw = os.getenv("DATABASE_URL", "")
    if not url_raw:
        sys.exit("ERROR: DATABASE_URL no está configurada. No se usará SQLite.")
    try:
        url = make_url(url_raw)
    except Exception as exc:
        sys.exit(f"ERROR: DATABASE_URL inválida: {exc}")
    if not url.drivername.startswith("mysql") or not (url.database or "").endswith("_pruebas"):
        sys.exit("ERROR: usar exclusivamente una base MariaDB cuyo nombre termine en '_pruebas'.")

    from backend.app import create_app
    from backend.app.extensions import db
    from backend.app.models import (
        Rol, Usuario, PerfilCuidador, Mascota, Solicitud,
        SolicitudMascota, HistorialEstado, Incidencia, Valoracion,
    )

    app = create_app("dev")
    app.config.update(TESTING=True)
    sufijo = uuid4().hex[:12]
    correo_dueno = f"finalizacion.dueno.{sufijo}@example.com"
    correo_cuidador = f"finalizacion.cuidador.{sufijo}@example.com"
    password = "PruebaFinalizacion2026!"
    ids = {}
    try:
        with app.app_context():
            if db.engine.dialect.name != "mysql" or db.engine.url.database != url.database:
                raise AssertionError("La conexión de Flask no corresponde a la MariaDB de pruebas.")
            rol_dueno = db.session.query(Rol).filter_by(nombre="DUENO").one()
            rol_cuidador = db.session.query(Rol).filter_by(nombre="CUIDADOR").one()
            dueno = Usuario(nombre="Dueno", apellido="Prueba", email=correo_dueno,
                            telefono="000000", provincia="Santa Fe", localidad="Santa Fe",
                            rol_id=rol_dueno.id, activo=True)
            cuidador = Usuario(nombre="Cuidador", apellido="Prueba", email=correo_cuidador,
                               telefono="000000", provincia="Santa Fe", localidad="Santa Fe",
                               rol_id=rol_cuidador.id, activo=True)
            dueno.set_password(password)
            cuidador.set_password(password)
            db.session.add_all([dueno, cuidador])
            db.session.flush()
            ids["dueno"] = dueno.id
            ids["cuidador"] = cuidador.id
            perfil = PerfilCuidador(usuario_id=cuidador.id, capacidad_maxima=1,
                                    admite_perros=True, admite_gatos=False, tarifa_diaria=100)
            mascota = Mascota(dueno_id=dueno.id, nombre="Mascota Histórica", especie="PERRO", tamano="CHICO")
            db.session.add_all([perfil, mascota])
            db.session.flush()
            ids["perfil"] = perfil.id
            ids["mascota"] = mascota.id
            solicitud = Solicitud(dueno_id=dueno.id, cuidador_id=perfil.id,
                                  modalidad="ALOJAMIENTO",
                                  fecha_desde=date.today()-timedelta(days=3),
                                  fecha_hasta=date.today()-timedelta(days=1),
                                  estado="ACEPTADA", total_mascotas=1,
                                  monto_total=200, contacto_emergencia="Contacto ficticio",
                                  autorizacion_urgencia=False)
            db.session.add(solicitud)
            db.session.flush()
            ids["solicitud"] = solicitud.id
            db.session.add(SolicitudMascota(solicitud_id=solicitud.id, mascota_id=mascota.id,
                                            nombre_snapshot="Mascota Histórica", especie_snapshot="PERRO"))
            db.session.add_all([
                HistorialEstado(solicitud_id=solicitud.id, usuario_id=dueno.id,
                                estado_anterior=None, estado_nuevo="PENDIENTE"),
                HistorialEstado(solicitud_id=solicitud.id, usuario_id=cuidador.id,
                                estado_anterior="PENDIENTE", estado_nuevo="ACEPTADA"),
            ])
            db.session.commit()

        client = app.test_client()
        csrf_response = client.get("/api/auth/csrf-token")
        assert csrf_response.status_code == 200, csrf_response.get_json()
        token = csrf_response.get_json()["csrf_token"]
        headers = {"X-CSRFToken": token}
        login = client.post("/api/auth/login", json={"email": correo_cuidador, "password": password}, headers=headers)
        assert login.status_code == 200, (login.status_code, login.get_json())
        print("[OK] Autenticación del cuidador en MariaDB de pruebas")
        sid = ids["solicitud"]
        fin = client.post(f"/api/solicitudes/{sid}/finalizar", headers=headers)
        assert fin.status_code == 200, (fin.status_code, fin.get_json())
        assert fin.get_json()["solicitud"]["estado"] == "FINALIZADA"
        print("[OK] Finalización HTTP 200, estado FINALIZADA")
        detalle = client.get(f"/api/solicitudes/{sid}")
        assert detalle.status_code == 200, detalle.get_json()
        estados = [h["estado_nuevo"] for h in detalle.get_json()["solicitud"]["historial"]]
        assert estados == ["PENDIENTE", "ACEPTADA", "FINALIZADA"], estados
        print("[OK] Historial PENDIENTE -> ACEPTADA -> FINALIZADA")
        repetida = client.post(f"/api/solicitudes/{sid}/finalizar", headers=headers)
        assert repetida.status_code == 409, (repetida.status_code, repetida.get_json())
        print("[OK] Segunda finalización rechazada HTTP 409")
        with app.app_context():
            db.session.expire_all()
            guardada = db.session.get(Solicitud, sid)
            assert guardada and guardada.estado == "FINALIZADA"
            print("[OK] Estado persistido en MariaDB")
        print("TODAS LAS PRUEBAS PASARON")
    finally:
        if ids:
            with app.app_context():
                try:
                    db.session.rollback()
                    sid = ids.get("solicitud")
                    if sid:
                        db.session.query(Valoracion).filter_by(solicitud_id=sid).delete(synchronize_session=False)
                        db.session.query(Incidencia).filter_by(solicitud_id=sid).delete(synchronize_session=False)
                        db.session.query(HistorialEstado).filter_by(solicitud_id=sid).delete(synchronize_session=False)
                        db.session.query(SolicitudMascota).filter_by(solicitud_id=sid).delete(synchronize_session=False)
                        db.session.query(Solicitud).filter_by(id=sid).delete(synchronize_session=False)
                    if ids.get("mascota"):
                        db.session.query(Mascota).filter_by(id=ids["mascota"]).delete(synchronize_session=False)
                    if ids.get("perfil"):
                        db.session.query(PerfilCuidador).filter_by(id=ids["perfil"]).delete(synchronize_session=False)
                    for name in ("dueno", "cuidador"):
                        if ids.get(name):
                            db.session.query(Usuario).filter_by(id=ids[name]).delete(synchronize_session=False)
                    db.session.commit()
                    print("[OK] Datos ficticios eliminados de la base de pruebas")
                except Exception as exc:
                    db.session.rollback()
                    print(f"ADVERTENCIA: la limpieza falló: {exc}. Revisá los IDs ficticios: {ids}", file=sys.stderr)
                    raise


if __name__ == "__main__":
    main()
