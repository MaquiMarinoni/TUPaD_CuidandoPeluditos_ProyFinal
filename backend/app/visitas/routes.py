
from datetime import date
from decimal import Decimal

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError

from backend.app.extensions import db
from backend.app.models import (
    Mascota,
    PerfilCuidador,
    Solicitud,
    SolicitudMascota,
)

from backend.app.solicitudes.routes import (
    bloquear_mascotas,
    registrar_estado,
    solicitud_a_dict,
)

from .logica import (
    conflicto_mascotas_visita,
    fecha_visita,
    hora_visita,
    horario_cubierto,
    turnos_superpuestos,
)


visitas_bp = Blueprint(
    "visitas",
    __name__,
    url_prefix="/api/visitas"
)

CAMPOS = {
    "cuidador_id",
    "fecha",
    "hora_desde",
    "hora_hasta",
    "mascotas_ids",
    "direccion_servicio",
    "contacto_emergencia",
    "veterinario_emergencia",
    "autorizacion_urgencia",
    "limite_gastos_urgencia",
}


def error(mensaje, codigo=400):
    return jsonify({"error": mensaje}), codigo


def validar(datos):
    if not isinstance(datos, dict):
        raise ValueError("Se requiere un objeto JSON.")

    if set(datos) - CAMPOS:
        raise ValueError("Se enviaron campos no permitidos.")

    cuidador_id = datos.get("cuidador_id")

    if type(cuidador_id) is not int or cuidador_id <= 0:
        raise ValueError("El cuidador_id no es valido.")

    fecha = fecha_visita(datos.get("fecha"))
    inicio = hora_visita(datos.get("hora_desde"))
    fin = hora_visita(datos.get("hora_hasta"))

    if fin <= inicio:
        raise ValueError("La hora final debe ser posterior al inicio.")

    if fecha < date.today():
        raise ValueError("No se permiten visitas en fechas pasadas.")

    ids = datos.get("mascotas_ids")

    if (
        not isinstance(ids, list)
        or not 1 <= len(ids) <= 20
        or any(type(i) is not int or i <= 0 for i in ids)
        or len(ids) != len(set(ids))
    ):
        raise ValueError("La lista de mascotas no es valida.")

    direccion = datos.get("direccion_servicio")

    if (
        not isinstance(direccion, str)
        or not direccion.strip()
        or len(direccion.strip()) > 120
    ):
        raise ValueError("La direccion del servicio es obligatoria.")

    contacto = datos.get("contacto_emergencia")

    if (
        not isinstance(contacto, str)
        or not contacto.strip()
        or len(contacto.strip()) > 100
    ):
        raise ValueError("El contacto de emergencia es obligatorio.")

    autorizacion = datos.get("autorizacion_urgencia")

    if type(autorizacion) is not bool:
        raise ValueError("Indica la autorizacion de urgencia.")

    veterinario = datos.get("veterinario_emergencia")

    if veterinario is not None:
        if not isinstance(veterinario, str):
            raise ValueError("El veterinario no es valido.")

        veterinario = veterinario.strip() or None

        if veterinario and len(veterinario) > 100:
            raise ValueError("El veterinario es demasiado largo.")

    limite = datos.get("limite_gastos_urgencia")

    if autorizacion:
        if not veterinario or limite is None:
            raise ValueError(
                "Indica veterinario y limite de gastos."
            )

        if isinstance(limite, bool) or not isinstance(
            limite, (str, int, float)
        ):
            raise ValueError("El limite de gastos no es valido.")

        try:
            limite = Decimal(str(limite))
        except Exception:
            raise ValueError("El limite de gastos no es valido.")

        if (
            not limite.is_finite()
            or limite <= 0
            or limite > Decimal("99999999.99")
            or limite != limite.quantize(Decimal("0.01"))
        ):
            raise ValueError("El limite de gastos no es valido.")

    elif limite is not None:
        raise ValueError(
            "No indiques gastos sin autorizacion."
        )

    return {
        "cuidador_id": cuidador_id,
        "fecha": fecha,
        "hora_desde": inicio,
        "hora_hasta": fin,
        "mascotas_ids": ids,
        "direccion_servicio": direccion.strip(),
        "contacto_emergencia": contacto.strip(),
        "veterinario_emergencia": veterinario,
        "autorizacion_urgencia": autorizacion,
        "limite_gastos_urgencia": limite,
    }


@visitas_bp.post("")
@login_required
def crear_visita():
    if not current_user.activo or not current_user.es_dueno():
        return error("Solo los dueños pueden solicitar visitas.", 403)

    try:
        datos = validar(request.get_json(silent=True))
    except ValueError as exc:
        return error(str(exc))

    try:
        perfil = db.session.execute(
            select(PerfilCuidador).where(
                PerfilCuidador.id == datos["cuidador_id"]
            ).with_for_update()
        ).scalar_one_or_none()

        if perfil is None or not perfil.usuario.activo:
            db.session.rollback()
            return error("Cuidador no encontrado.", 404)

        if perfil.tarifa_visita is None:
            db.session.rollback()
            return error("El cuidador no ofrece visitas.", 409)

        if not horario_cubierto(
            perfil.id,
            datos["fecha"],
            datos["hora_desde"],
            datos["hora_hasta"],
        ):
            db.session.rollback()
            return error("El horario no esta disponible.", 409)

        mascotas = db.session.execute(
            select(Mascota).where(
                Mascota.id.in_(datos["mascotas_ids"]),
                Mascota.dueno_id == current_user.id,
                Mascota.activo.is_(True),
            )
        ).scalars().all()

        if len(mascotas) != len(datos["mascotas_ids"]):
            db.session.rollback()
            return error("Alguna mascota no te pertenece.", 403)

        for mascota in mascotas:
            if mascota.especie == "PERRO" and not perfil.admite_perros:
                db.session.rollback()
                return error("El cuidador no admite perros.")

            if mascota.especie == "GATO" and not perfil.admite_gatos:
                db.session.rollback()
                return error("El cuidador no admite gatos.")

        bloquear_mascotas(datos["mascotas_ids"])

        if turnos_superpuestos(
            perfil.id,
            datos["fecha"],
            datos["hora_desde"],
            datos["hora_hasta"],
        ):
            db.session.rollback()
            return error("El cuidador ya tiene una visita.", 409)

        if conflicto_mascotas_visita(
            datos["mascotas_ids"],
            datos["fecha"],
            datos["hora_desde"],
            datos["hora_hasta"],
        ):
            db.session.rollback()
            return error("Una mascota ya tiene un servicio.", 409)

        solicitud = Solicitud(
            dueno_id=current_user.id,
            cuidador_id=perfil.id,
            modalidad="VISITA",
            fecha_desde=datos["fecha"],
            fecha_hasta=datos["fecha"],
            hora_desde=datos["hora_desde"],
            hora_hasta=datos["hora_hasta"],
            estado="PENDIENTE",
            total_mascotas=len(mascotas),
            monto_total=perfil.tarifa_visita,
            contacto_emergencia=datos["contacto_emergencia"],
            veterinario_emergencia=datos["veterinario_emergencia"],
            autorizacion_urgencia=datos["autorizacion_urgencia"],
            limite_gastos_urgencia=datos["limite_gastos_urgencia"],
            direccion_servicio=datos["direccion_servicio"],
        )

        for mascota in mascotas:
            solicitud.mascotas_asociadas.append(
                SolicitudMascota(
                    mascota_id=mascota.id,
                    nombre_snapshot=mascota.nombre,
                    especie_snapshot=mascota.especie,
                    cuidados_snapshot=mascota.cuidados_especiales,
                    veterinario_snapshot=mascota.contacto_veterinario,
                )
            )

        registrar_estado(solicitud, None, "PENDIENTE")
        db.session.add(solicitud)
        db.session.commit()

        return jsonify({
            "mensaje": "Visita solicitada correctamente.",
            "solicitud": solicitud_a_dict(solicitud),
        }), 201

    except (IntegrityError, OperationalError):
        db.session.rollback()
        return error("No se pudo registrar la visita.", 409)
