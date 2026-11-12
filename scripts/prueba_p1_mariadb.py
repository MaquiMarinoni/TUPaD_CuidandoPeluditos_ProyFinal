"""Prueba P1 HTTP+persistencia en MariaDB aislada (_pruebas).

Desde la raiz: python -m scripts.prueba_p1_mariadb
No cambia tablas ni datos anteriores; crea y elimina entidades propias.
"""
import os
import sys
from datetime import date, timedelta
from pathlib import Path
from uuid import uuid4

from sqlalchemy.engine import make_url


def main():
    raw = os.environ.get("DATABASE_URL", "")
    if not raw:
        sys.exit("ERROR: DATABASE_URL no está configurada; no se permite SQLite.")
    try:
        url = make_url(raw)
    except Exception:
        sys.exit("ERROR: DATABASE_URL tiene un formato inválido.")
    if not url.drivername.startswith("mysql") or not (url.database or "").endswith("_pruebas"):
        sys.exit("ERROR: esta prueba solo admite MySQL/MariaDB en una base terminada en _pruebas.")

    from backend.app import create_app
    from backend.app.extensions import db
    from backend.app.models import (
        Rol, Usuario, PerfilCuidador, Mascota, Solicitud,
        SolicitudMascota, HistorialEstado, Incidencia, Valoracion,
    )

    app = create_app("dev")
    app.config.update(TESTING=True)
    prefix = uuid4().hex[:12]
    pwd = "PruebasLocalesP1-2026!"
    emails = {k: f"p1.{k}.{prefix}@example.com" for k in ("dueno", "cuidador", "ajeno")}
    ids = {}
    checks = []
    success = False
    cleanup_ok = False

    def check(description, condition):
        if not condition:
            raise AssertionError(f"FALLO: {description}")
        line = f"[OK] {description}"
        print(line, flush=True)
        checks.append(line)

    def result_code(response, code, detail):
        check(f"{detail}: HTTP {code}", response.status_code == code)
        return response.get_json()

    def session_client(email):
        client = app.test_client()
        t = client.get("/api/auth/csrf-token")
        check("Token CSRF disponible", t.status_code == 200 and bool((t.get_json() or {}).get("csrf_token")))
        token = t.get_json()["csrf_token"]
        headers = {"X-CSRFToken": token}
        r = client.post("/api/auth/login", json={"email": email, "password": pwd}, headers=headers)
        result_code(r, 200, "Inicio de sesión de usuario ficticio")
        return client, headers

    try:
        with app.app_context():
            check("Motor MariaDB/MySQL y base _pruebas verificados",
                  db.engine.dialect.name == "mysql" and db.engine.url.database == url.database)
            roles = {}
            for name in ("DUENO", "CUIDADOR"):
                roles[name] = db.session.query(Rol).filter_by(nombre=name).one()
            users = {}
            for key, rolname in (("dueno", "DUENO"), ("cuidador", "CUIDADOR"), ("ajeno", "DUENO")):
                user = Usuario(nombre="P1", apellido="Ficticio", email=emails[key],
                               telefono="000000", provincia="Santa Fe", localidad="Santa Fe",
                               rol_id=roles[rolname].id, activo=True)
                user.set_password(pwd)
                db.session.add(user)
                users[key] = user
            db.session.flush()
            ids.update({key: users[key].id for key in users})
            profile = PerfilCuidador(usuario_id=users["cuidador"].id, capacidad_maxima=2,
                                     admite_perros=True, admite_gatos=True, tarifa_diaria=1000)
            pet = Mascota(dueno_id=users["dueno"].id, nombre="P1 Mascota Ficticia",
                          especie="PERRO", tamano="CHICO")
            db.session.add_all([profile, pet])
            db.session.flush()
            ids["perfil"] = profile.id
            ids["mascota"] = pet.id
            today = date.today()
            active = Solicitud(dueno_id=users["dueno"].id, cuidador_id=profile.id,
                               modalidad="ALOJAMIENTO", fecha_desde=today - timedelta(days=1),
                               fecha_hasta=today + timedelta(days=1), estado="ACEPTADA",
                               total_mascotas=1, monto_total=2000,
                               contacto_emergencia="Contacto ficticio", autorizacion_urgencia=False)
            done = Solicitud(dueno_id=users["dueno"].id, cuidador_id=profile.id,
                             modalidad="ALOJAMIENTO", fecha_desde=today-timedelta(days=4),
                             fecha_hasta=today-timedelta(days=2), estado="FINALIZADA",
                             total_mascotas=1, monto_total=2000,
                             contacto_emergencia="Contacto ficticio", autorizacion_urgencia=False)
            db.session.add_all([active, done])
            db.session.flush()
            ids["activa"] = active.id
            ids["final"] = done.id
            db.session.add_all([
                SolicitudMascota(solicitud_id=active.id, mascota_id=pet.id,
                                 nombre_snapshot=pet.nombre, especie_snapshot="PERRO"),
                SolicitudMascota(solicitud_id=done.id, mascota_id=pet.id,
                                 nombre_snapshot=pet.nombre, especie_snapshot="PERRO"),
            ])
            db.session.commit()

        caregiver, ch = session_client(emails["cuidador"])
        owner, oh = session_client(emails["dueno"])
        outsider, xh = session_client(emails["ajeno"])
        sid = ids["activa"]
        payload = {"solicitud_id": sid, "tipo": "SALUD",
                   "descripcion": "Control veterinario ficticio durante el servicio.",
                   "medidas_tomadas": "Se informó al dueño."}
        created = caregiver.post("/api/incidencias", json=payload, headers=ch)
        data = result_code(created, 201, "Cuidador registra incidencia")
        iid = data["incidencia"]["id"]
        ids["incidencia"] = iid
        check("Incidencia inicial ABIERTA", data["incidencia"]["estado"] == "ABIERTA")
        owner_read = owner.get(f"/api/incidencias?solicitud_id={sid}")
        data = result_code(owner_read, 200, "Dueño consulta incidencias")
        check("Incidencia consultable por dueño", any(i["id"] == iid for i in data["incidencias"]))
        result_code(outsider.get(f"/api/incidencias?solicitud_id={sid}"), 404,
                    "Tercero no puede consultar incidencias")
        result_code(owner.patch(f"/api/incidencias/{iid}/resolver", json={"medidas_tomadas": "X"}, headers=oh),
                    403, "Dueño no puede resolver incidencia")
        resolved = caregiver.patch(f"/api/incidencias/{iid}/resolver",
                                   json={"medidas_tomadas": "Atención ficticia completada."}, headers=ch)
        data = result_code(resolved, 200, "Cuidador resuelve incidencia")
        check("Incidencia final RESUELTA", data["incidencia"]["estado"] == "RESUELTA")
        result_code(caregiver.patch(f"/api/incidencias/{iid}/resolver",
                                    json={"medidas_tomadas": "Repetir"}, headers=ch),
                    409, "No admite segunda resolución")
        result_code(owner.post("/api/incidencias", json=payload, headers=oh), 403,
                    "Dueño no puede reportar incidencia")

        final_id = ids["final"]
        rating_payload = {"solicitud_id": final_id, "puntaje": 5,
                          "comentario": "Valoración ficticia de prueba."}
        rating = owner.post("/api/valoraciones", json=rating_payload, headers=oh)
        data = result_code(rating, 201, "Dueño valora servicio finalizado")
        ids["valoracion"] = data["valoracion"]["id"]
        check("Puntaje guardado", data["valoracion"]["puntaje"] == 5)
        listing = owner.get(f"/api/valoraciones?cuidador_id={ids['perfil']}")
        data = result_code(listing, 200, "Listado público de valoraciones")
        # El perfil es nuevo, por lo tanto su única valoración debe ser nuestra prueba.
        check("Cantidad y promedio correctos", data["resumen"]["cantidad"] == 1 and data["resumen"]["promedio"] == 5.0)
        result_code(owner.get(f"/api/valoraciones/resumen/{ids['perfil']}"), 200,
                    "Consulta del promedio público")
        result_code(owner.post("/api/valoraciones", json=rating_payload, headers=oh), 409,
                    "No admite doble valoración")
        result_code(caregiver.post("/api/valoraciones", json=rating_payload, headers=ch), 403,
                    "Cuidador no puede valorar")
        result_code(outsider.post("/api/valoraciones", json=rating_payload, headers=xh), 404,
                    "Otro dueño no puede valorar una solicitud ajena")
        result_code(owner.post("/api/valoraciones", json={"solicitud_id": sid, "puntaje": 5}, headers=oh),
                    409, "No se valora servicio no finalizado")

        with app.app_context():
            db.session.expire_all()
            i = db.session.get(Incidencia, iid)
            v = db.session.get(Valoracion, ids["valoracion"])
            check("Incidencia RESUELTA persistida en MariaDB", i is not None and i.estado == "RESUELTA")
            check("Valoración de 5 estrellas persistida en MariaDB", v is not None and v.puntaje == 5)
        success = True
    finally:
        if ids:
            with app.app_context():
                try:
                    db.session.rollback()
                    for sid in (ids.get("activa"), ids.get("final")):
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
                    for key in ("dueno", "cuidador", "ajeno"):
                        if ids.get(key):
                            db.session.query(Usuario).filter_by(id=ids[key]).delete(synchronize_session=False)
                    db.session.commit()
                    cleanup_ok = True
                    print("[OK] Datos ficticios eliminados de MariaDB de pruebas", flush=True)
                except Exception as exc:
                    db.session.rollback()
                    print(f"ERROR EN LIMPIEZA: {type(exc).__name__}: {exc}; IDs: {ids}", file=sys.stderr)
                    raise

    if success and cleanup_ok:
        print("TODAS LAS PRUEBAS P1 PASARON", flush=True)
        evidence = Path("docs/evidencias/p1-mariadb-2026-11-12.txt")
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text(
            "Cuidando Peluditos - Prueba P1 MariaDB - 12/11/2026\n"
            "Motor MariaDB/MySQL, base aislada _pruebas. Ejecución local con Flask test_client.\n"
            "Script: python -m scripts.prueba_p1_mariadb\n"
            + "\n".join(checks)
            + "\n[OK] Limpieza de entidades ficticias\nTODAS LAS PRUEBAS P1 PASARON\n",
            encoding="utf-8",
        )
        print(f"[OK] Evidencia creada: {evidence}")
    else:
        sys.exit("ERROR: prueba o limpieza incompleta.")


if __name__ == "__main__":
    main()
