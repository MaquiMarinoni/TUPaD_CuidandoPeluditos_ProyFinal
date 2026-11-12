"""Registro y consulta de incidencias de servicios."""
from datetime import date

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import select

from backend.app.extensions import db
from backend.app.models import Incidencia, Solicitud

incidencias_bp = Blueprint("incidencias", __name__, url_prefix="/api/incidencias")
TIPOS = {"SALUD", "CONDUCTA", "EXTRAVIO", "OTRO"}
CAMPOS_CREAR = {"solicitud_id", "tipo", "descripcion", "medidas_tomadas"}
CAMPOS_RESOLVER = {"medidas_tomadas"}


def fallo(mensaje, codigo=400):
    return jsonify({"error": mensaje}), codigo


def es_participante(solicitud):
    return (
        current_user.activo
        and (
            solicitud.dueno_id == current_user.id
            or solicitud.cuidador_perfil.usuario_id == current_user.id
        )
    )


def es_cuidador_asignado(solicitud):
    return (
        current_user.activo
        and current_user.es_cuidador()
        and solicitud.cuidador_perfil.usuario_id == current_user.id
    )


def incidencia_a_dict(incidencia):
    return {
        "id": incidencia.id,
        "solicitud_id": incidencia.solicitud_id,
        "reportado_por_id": incidencia.reportado_por_id,
        "tipo": incidencia.tipo,
        "descripcion": incidencia.descripcion,
        "medidas_tomadas": incidencia.medidas_tomadas,
        "estado": incidencia.estado,
        "fecha_registro": incidencia.fecha_registro.isoformat() if incidencia.fecha_registro else None,
    }


def texto(datos, nombre, obligatorio=False, longitud=2000):
    valor = datos.get(nombre)
    if valor is None and not obligatorio:
        return None
    if not isinstance(valor, str) or (obligatorio and not valor.strip()):
        raise ValueError(f"El campo {nombre} debe contener texto.")
    valor = valor.strip()
    if len(valor) > longitud:
        raise ValueError(f"El campo {nombre} supera los {longitud} caracteres.")
    return valor or None


@incidencias_bp.get("")
@login_required
def listar():
    solicitud_id = request.args.get("solicitud_id", type=int)
    if solicitud_id is None or solicitud_id <= 0:
        return fallo("Indica un solicitud_id entero positivo.")
    solicitud = db.session.get(Solicitud, solicitud_id)
    if solicitud is None or not es_participante(solicitud):
        return fallo("Solicitud no encontrada.", 404)
    registros = db.session.scalars(
        select(Incidencia)
        .where(Incidencia.solicitud_id == solicitud_id)
        .order_by(Incidencia.id.desc())
    ).all()
    return jsonify({"incidencias": [incidencia_a_dict(i) for i in registros]}), 200


@incidencias_bp.get("/<int:incidencia_id>")
@login_required
def detalle(incidencia_id):
    incidencia = db.session.get(Incidencia, incidencia_id)
    if incidencia is None or not es_participante(incidencia.solicitud):
        return fallo("Incidencia no encontrada.", 404)
    return jsonify({"incidencia": incidencia_a_dict(incidencia)}), 200


@incidencias_bp.post("")
@login_required
def crear():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict) or set(datos) - CAMPOS_CREAR:
        return fallo("Datos JSON invalidos o campos no permitidos.")
    sid = datos.get("solicitud_id")
    if type(sid) is not int or sid <= 0:
        return fallo("solicitud_id debe ser un entero positivo.")
    solicitud = db.session.get(Solicitud, sid)
    if solicitud is None or not es_participante(solicitud):
        return fallo("Solicitud no encontrada.", 404)
    if not es_cuidador_asignado(solicitud):
        return fallo("Solo el cuidador asignado puede reportar incidencias.", 403)
    if solicitud.estado != "ACEPTADA":
        return fallo("La solicitud debe estar ACEPTADA para reportar incidencias.", 409)
    hoy = date.today()
    if not solicitud.fecha_desde <= hoy <= solicitud.fecha_hasta:
        return fallo("Solo se pueden reportar incidencias durante las fechas del servicio.", 409)
    tipo = datos.get("tipo")
    if not isinstance(tipo, str) or tipo not in TIPOS:
        return fallo("Tipo invalido: SALUD, CONDUCTA, EXTRAVIO u OTRO.")
    try:
        descripcion = texto(datos, "descripcion", obligatorio=True)
        medidas = texto(datos, "medidas_tomadas")
    except ValueError as exc:
        return fallo(str(exc))
    incidencia = Incidencia(
        solicitud_id=sid,
        reportado_por_id=current_user.id,
        tipo=tipo,
        descripcion=descripcion,
        medidas_tomadas=medidas,
        estado="ABIERTA",
    )
    db.session.add(incidencia)
    db.session.commit()
    return jsonify({"mensaje": "Incidencia registrada.", "incidencia": incidencia_a_dict(incidencia)}), 201


@incidencias_bp.patch("/<int:incidencia_id>/resolver")
@login_required
def resolver(incidencia_id):
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict) or set(datos) - CAMPOS_RESOLVER:
        return fallo("Datos JSON invalidos o campos no permitidos.")
    try:
        medidas = texto(datos, "medidas_tomadas", obligatorio=True)
    except ValueError as exc:
        return fallo(str(exc))
    incidencia = db.session.scalar(
        select(Incidencia).where(Incidencia.id == incidencia_id).with_for_update()
    )
    if incidencia is None or not es_participante(incidencia.solicitud):
        db.session.rollback()
        return fallo("Incidencia no encontrada.", 404)
    if not es_cuidador_asignado(incidencia.solicitud):
        db.session.rollback()
        return fallo("Solo el cuidador asignado puede resolver incidencias.", 403)
    if incidencia.estado != "ABIERTA":
        db.session.rollback()
        return fallo("La incidencia ya fue resuelta.", 409)
    incidencia.medidas_tomadas = medidas
    incidencia.estado = "RESUELTA"
    db.session.commit()
    return jsonify({"mensaje": "Incidencia resuelta.", "incidencia": incidencia_a_dict(incidencia)}), 200
