"""Valoraciones verificadas de servicios finalizados."""
from decimal import Decimal

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from backend.app.extensions import db
from backend.app.models import Solicitud, Valoracion, PerfilCuidador


valoraciones_bp = Blueprint("valoraciones", __name__, url_prefix="/api/valoraciones")


def fallo(mensaje, codigo=400):
    return jsonify({"error": mensaje}), codigo


def valoracion_a_dict(v):
    return {
        "id": v.id,
        "solicitud_id": v.solicitud_id,
        "cuidador_id": v.cuidador_id,
        "puntaje": v.puntaje,
        "comentario": v.comentario,
        "fecha_creacion": v.fecha_creacion.isoformat() if v.fecha_creacion else None,
    }


def resumen(cuidador_id):
    cantidad, promedio = db.session.query(
        func.count(Valoracion.id), func.avg(Valoracion.puntaje)
    ).filter(Valoracion.cuidador_id == cuidador_id).one()
    return {
        "cuidador_id": cuidador_id,
        "cantidad": int(cantidad),
        "promedio": round(float(promedio), 2) if promedio is not None else None,
    }


@valoraciones_bp.post("")
@login_required
def crear():
    if not current_user.activo or not current_user.es_dueno():
        return fallo("Solo el dueno puede valorar un servicio.", 403)

    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return fallo("Se requieren datos JSON validos.")
    if set(datos) - {"solicitud_id", "puntaje", "comentario"}:
        return fallo("Se enviaron campos no permitidos.")

    solicitud_id = datos.get("solicitud_id")
    puntaje = datos.get("puntaje")
    comentario = datos.get("comentario")
    if type(solicitud_id) is not int or solicitud_id <= 0:
        return fallo("solicitud_id no es valido.")
    if type(puntaje) is not int or not 1 <= puntaje <= 5:
        return fallo("El puntaje debe ser un entero de 1 a 5.")
    if comentario is not None:
        if not isinstance(comentario, str):
            return fallo("El comentario debe ser texto.")
        comentario = comentario.strip() or None
        if comentario is not None and len(comentario) > 2000:
            return fallo("El comentario no puede superar 2000 caracteres.")

    solicitud = db.session.get(Solicitud, solicitud_id)
    if solicitud is None or solicitud.dueno_id != current_user.id:
        return fallo("Solicitud no encontrada.", 404)
    if solicitud.estado != "FINALIZADA":
        return fallo("Solo se pueden valorar servicios finalizados.", 409)
    if Valoracion.query.filter_by(solicitud_id=solicitud.id).first():
        return fallo("Esta solicitud ya tiene una valoracion.", 409)

    valoracion = Valoracion(
        solicitud_id=solicitud.id,
        dueno_id=current_user.id,
        cuidador_id=solicitud.cuidador_id,
        puntaje=puntaje,
        comentario=comentario,
    )
    try:
        db.session.add(valoracion)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return fallo("Esta solicitud ya tiene una valoracion.", 409)

    return jsonify({"mensaje": "Valoracion registrada.", "valoracion": valoracion_a_dict(valoracion)}), 201


@valoraciones_bp.get("")
def listar():
    cuidador_id = request.args.get("cuidador_id", type=int)
    if cuidador_id is None or cuidador_id <= 0:
        return fallo("Indica cuidador_id valido.")
    perfil = db.session.get(PerfilCuidador, cuidador_id)
    if perfil is None:
        return fallo("Cuidador no encontrado.", 404)
    valoraciones = Valoracion.query.filter_by(cuidador_id=cuidador_id).order_by(
        Valoracion.id.desc()
    ).all()
    return jsonify({
        "valoraciones": [valoracion_a_dict(v) for v in valoraciones],
        "resumen": resumen(cuidador_id),
    }), 200


@valoraciones_bp.get("/resumen/<int:cuidador_id>")
def obtener_resumen(cuidador_id):
    perfil = db.session.get(PerfilCuidador, cuidador_id)
    if perfil is None:
        return fallo("Cuidador no encontrado.", 404)
    return jsonify({"resumen": resumen(cuidador_id)}), 200
