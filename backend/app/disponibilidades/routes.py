
from datetime import date, datetime, time

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from backend.app.extensions import db
from backend.app.models import Disponibilidad, PerfilCuidador

from backend.app.integridad_reservas import (
    afecta_reserva_aceptada,
)

disponibilidades_bp = Blueprint(
    "disponibilidades",
    __name__,
    url_prefix="/api/disponibilidades"
)

MODALIDADES = {"ALOJAMIENTO", "VISITA"}

CAMPOS_PERMITIDOS = {
    "modalidad",
    "fecha_desde",
    "fecha_hasta",
    "hora_desde",
    "hora_hasta",
}


def error(mensaje, codigo=400):
    return jsonify({"error": mensaje}), codigo


def disponibilidad_a_dict(disponibilidad):
    return {
        "id": disponibilidad.id,
        "cuidador_id": disponibilidad.cuidador_id,
        "modalidad": disponibilidad.modalidad,
        "fecha_desde": disponibilidad.fecha_desde.isoformat(),
        "fecha_hasta": disponibilidad.fecha_hasta.isoformat(),
        "hora_desde": (
            disponibilidad.hora_desde.strftime("%H:%M")
            if disponibilidad.hora_desde else None
        ),
        "hora_hasta": (
            disponibilidad.hora_hasta.strftime("%H:%M")
            if disponibilidad.hora_hasta else None
        ),
        "activo": disponibilidad.activo,
    }


def obtener_perfil_propio():
    if not current_user.activo or not current_user.es_cuidador():
        return None

    return PerfilCuidador.query.filter_by(
        usuario_id=current_user.id
    ).first()


def convertir_fecha(valor, campo):
    if not isinstance(valor, str):
        raise ValueError(f"El campo {campo} debe ser una fecha.")

    try:
        fecha = date.fromisoformat(valor)
        if fecha.isoformat() != valor:
            raise ValueError()
        return fecha
    except ValueError:
        raise ValueError(
            f"El campo {campo} debe tener formato AAAA-MM-DD."
        )


def convertir_hora(valor, campo):
    if not isinstance(valor, str):
        raise ValueError(f"El campo {campo} debe ser una hora.")

    try:
        hora = datetime.strptime(valor, "%H:%M").time()
        if hora.strftime("%H:%M") != valor:
            raise ValueError()
        return hora
    except ValueError:
        raise ValueError(
            f"El campo {campo} debe tener formato HH:MM."
        )


def validar_datos(datos):
    if not isinstance(datos, dict):
        return None, "Se requieren datos JSON validos."

    if set(datos) - CAMPOS_PERMITIDOS:
        return None, "Se enviaron campos no permitidos."

    obligatorios = {"modalidad", "fecha_desde", "fecha_hasta"}

    if not obligatorios.issubset(datos):
        return None, "Faltan campos obligatorios."

    modalidad = datos["modalidad"]

    if not isinstance(modalidad, str):
        return None, "La modalidad no es valida."

    modalidad = modalidad.strip().upper()

    if modalidad not in MODALIDADES:
        return None, "La modalidad debe ser ALOJAMIENTO o VISITA."

    try:
        fecha_desde = convertir_fecha(datos["fecha_desde"], "fecha_desde")
        fecha_hasta = convertir_fecha(datos["fecha_hasta"], "fecha_hasta")
    except ValueError as exc:
        return None, str(exc)

    if fecha_desde < date.today():
        return None, "No se puede ofrecer disponibilidad en el pasado."

    if fecha_hasta < fecha_desde:
        return None, "La fecha final no puede ser anterior al inicio."

    # Limite para evitar periodos desmedidos.
    if (fecha_hasta - fecha_desde).days > 365:
        return None, "El periodo no puede superar 365 dias."

    hora_desde = None
    hora_hasta = None

    if modalidad == "ALOJAMIENTO":
        if fecha_hasta <= fecha_desde:
            return None, "El alojamiento requiere al menos una noche."

        if datos.get("hora_desde") is not None:
            return None, "El alojamiento no utiliza horarios."

        if datos.get("hora_hasta") is not None:
            return None, "El alojamiento no utiliza horarios."

    else:
        if datos.get("hora_desde") is None:
            return None, "La hora de inicio es obligatoria."

        if datos.get("hora_hasta") is None:
            return None, "La hora final es obligatoria."

        try:
            hora_desde = convertir_hora(datos["hora_desde"], "hora_desde")
            hora_hasta = convertir_hora(datos["hora_hasta"], "hora_hasta")
        except ValueError as exc:
            return None, str(exc)

        if hora_hasta <= hora_desde:
            return None, "La hora final debe ser posterior al inicio."

    return {
        "modalidad": modalidad,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "hora_desde": hora_desde,
        "hora_hasta": hora_hasta,
    }, None


def fechas_se_superponen(nueva, existente):
    if nueva["modalidad"] == "ALOJAMIENTO":
        # Los extremos de alojamiento representan:
        # [fecha_ingreso, fecha_salida)
        return (
            nueva["fecha_desde"] < existente.fecha_hasta
            and nueva["fecha_hasta"] > existente.fecha_desde
        )

    # Las visitas incluyen ambos dias del rango.
    return (
        nueva["fecha_desde"] <= existente.fecha_hasta
        and nueva["fecha_hasta"] >= existente.fecha_desde
    )


def hay_conflicto(perfil_id, nuevos_datos, excluir_id=None):
    consulta = Disponibilidad.query.filter_by(
        cuidador_id=perfil_id,
        modalidad=nuevos_datos["modalidad"],
        activo=True
    )

    if excluir_id is not None:
        consulta = consulta.filter(Disponibilidad.id != excluir_id)

    for existente in consulta.with_for_update().all():
        if not fechas_se_superponen(nuevos_datos, existente):
            continue

        if nuevos_datos["modalidad"] == "ALOJAMIENTO":
            return True

        # Las visitas chocan solo si se pisan fechas y horas.
        horas_superpuestas = (
            nuevos_datos["hora_desde"] < existente.hora_hasta
            and nuevos_datos["hora_hasta"] > existente.hora_desde
        )

        if horas_superpuestas:
            return True

    return False


@disponibilidades_bp.get("")
@login_required
def listar_mis_disponibilidades():
    perfil = obtener_perfil_propio()

    if perfil is None:
        return error("Necesitas un perfil de cuidador.", 403)

    registros = Disponibilidad.query.filter_by(
        cuidador_id=perfil.id,
        activo=True
    ).order_by(
        Disponibilidad.fecha_desde,
        Disponibilidad.hora_desde
    ).all()

    return jsonify({
        "disponibilidades": [
            disponibilidad_a_dict(d) for d in registros
        ]
    }), 200


@disponibilidades_bp.post("")
@login_required
def crear_disponibilidad():
    perfil = obtener_perfil_propio()

    if perfil is None:
        return error("Necesitas un perfil de cuidador.", 403)

    datos, mensaje = validar_datos(request.get_json(silent=True))

    if mensaje:
        return error(mensaje)

    if datos["modalidad"] == "VISITA" and perfil.tarifa_visita is None:
        return error("Primero configura una tarifa de visitas.")

    if datos["modalidad"] == "ALOJAMIENTO" and not (
        perfil.admite_perros or perfil.admite_gatos
    ):
        return error("Debes admitir al menos una especie.")

    # Bloquear el perfil para serializar cambios simultaneos
    # de disponibilidad realizados por el mismo cuidador.
    db.session.query(PerfilCuidador).filter_by(
        id=perfil.id
    ).with_for_update().first()

    if hay_conflicto(perfil.id, datos):
        db.session.rollback()
        return error(
            "Ya existe disponibilidad superpuesta para esa modalidad.",
            409
        )

    registro = Disponibilidad(
        cuidador_id=perfil.id,
        **datos
    )

    db.session.add(registro)
    db.session.commit()

    return jsonify({
        "mensaje": "Disponibilidad creada correctamente.",
        "disponibilidad": disponibilidad_a_dict(registro)
    }), 201


@disponibilidades_bp.put("/<int:disponibilidad_id>")
@login_required
def editar_disponibilidad(disponibilidad_id):
    perfil = obtener_perfil_propio()

    if perfil is None:
        return error("Necesitas un perfil de cuidador.", 403)

    # Primero bloqueamos el perfil; luego leemos el registro.
    db.session.query(PerfilCuidador).filter_by(
        id=perfil.id
    ).with_for_update().first()

    registro = Disponibilidad.query.filter_by(
        id=disponibilidad_id,
        cuidador_id=perfil.id,
        activo=True
    ).first()


    # De esta forma, primero comprobamos que la disponibilidad existe y pertenece al cuidador y luego verificamos si hay reservas comprometidas.
    if registro is None:
        db.session.rollback()
        return error("Disponibilidad no encontrada.", 404)

    if afecta_reserva_aceptada(registro):
        db.session.rollback()
        return error(
            "No podes modificar fechas que respaldan "
            "reservas aceptadas.",
            409
        )

    entrada = request.get_json(silent=True)

    if not isinstance(entrada, dict):
        db.session.rollback()
        return error("Se requieren datos JSON validos.")

    if set(entrada) - CAMPOS_PERMITIDOS:
        db.session.rollback()
        return error("Se enviaron campos no permitidos.")

    # Para editar se admiten campos parciales.
    datos_actuales = {
        "modalidad": registro.modalidad,
        "fecha_desde": registro.fecha_desde.isoformat(),
        "fecha_hasta": registro.fecha_hasta.isoformat(),
        "hora_desde": (
            registro.hora_desde.strftime("%H:%M")
            if registro.hora_desde else None
        ),
        "hora_hasta": (
            registro.hora_hasta.strftime("%H:%M")
            if registro.hora_hasta else None
        ),
    }

    datos_actuales.update(entrada)

    datos, mensaje = validar_datos(datos_actuales)

    if mensaje:
        db.session.rollback()
        return error(mensaje)

    if datos["modalidad"] == "VISITA" and perfil.tarifa_visita is None:
        db.session.rollback()
        return error("Primero configura una tarifa de visitas.")

    if hay_conflicto(perfil.id, datos, excluir_id=registro.id):
        db.session.rollback()
        return error("La disponibilidad se superpone con otra.", 409)

    for campo, valor in datos.items():
        setattr(registro, campo, valor)

    db.session.commit()

    return jsonify({
        "mensaje": "Disponibilidad actualizada correctamente.",
        "disponibilidad": disponibilidad_a_dict(registro)
    }), 200


@disponibilidades_bp.delete("/<int:disponibilidad_id>")
@login_required
def desactivar_disponibilidad(disponibilidad_id):
    perfil = obtener_perfil_propio()

    if perfil is None:
        return error("Necesitas un perfil de cuidador.", 403)

    db.session.query(PerfilCuidador).filter_by(
        id=perfil.id
    ).with_for_update().first()

    registro = Disponibilidad.query.filter_by(
        id=disponibilidad_id,
        cuidador_id=perfil.id,
        activo=True
    ).first()

    if registro is None:
        db.session.rollback()
        return error("Disponibilidad no encontrada.", 404)

    if afecta_reserva_aceptada(registro):
        db.session.rollback()
        return error(
            "No podes desactivar esta disponibilidad "
            "porque existen reservas aceptadas.",
            409
        )

    registro.activo = False
    db.session.commit()

    return jsonify({
        "mensaje": "Disponibilidad desactivada correctamente."
    }), 200
