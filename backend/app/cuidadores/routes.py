
from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from backend.app.extensions import db
from backend.app.models import PerfilCuidador, Usuario, Disponibilidad
from backend.app.disponibilidades.routes import disponibilidad_a_dict

from backend.app.integridad_reservas import (
    capacidad_suficiente,
    reservas_comprometidas,
)


cuidadores_bp = Blueprint(
    "cuidadores",
    __name__,
    url_prefix="/api/cuidadores"
)

CAMPOS_PERMITIDOS = {
    "descripcion",
    "capacidad_maxima",
    "admite_perros",
    "admite_gatos",
    "condiciones_convivencia",
    "tarifa_diaria",
    "tarifa_visita",
}


def responder_error(mensaje, codigo=400):
    return jsonify({"error": mensaje}), codigo


def es_cuidador():
    return current_user.activo and current_user.es_cuidador()


def perfil_a_dict(perfil):
    usuario = perfil.usuario

    return {
        "id": perfil.id,
        "usuario_id": usuario.id,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "provincia": usuario.provincia,
        "localidad": usuario.localidad,
        "descripcion": perfil.descripcion,
        "capacidad_maxima": perfil.capacidad_maxima,
        "admite_perros": perfil.admite_perros,
        "admite_gatos": perfil.admite_gatos,
        "condiciones_convivencia": perfil.condiciones_convivencia,
        "tarifa_diaria": str(perfil.tarifa_diaria),
        "tarifa_visita": (
            str(perfil.tarifa_visita)
            if perfil.tarifa_visita is not None
            else None
        ),
    }


def validar_precio(valor, campo):
    if isinstance(valor, bool) or valor is None:
        return None, f"El campo {campo} no es valido."

    if not isinstance(valor, (int, float, str)):
        return None, f"El campo {campo} no es valido."

    try:
        precio = Decimal(str(valor))
    except InvalidOperation:
        return None, f"El campo {campo} debe ser un numero."

    if not precio.is_finite() or precio <= 0:
        return None, f"El campo {campo} debe ser mayor que cero."

    if precio > Decimal("99999999.99"):
        return None, f"El campo {campo} supera el maximo permitido."

    if precio != precio.quantize(Decimal("0.01")):
        return None, f"El campo {campo} admite hasta dos decimales."

    return precio, None


def validar_datos(datos, creacion=False):
    if not isinstance(datos, dict) or not datos:
        return None, "Debes enviar datos JSON validos."

    if set(datos.keys()) - CAMPOS_PERMITIDOS:
        return None, "Se enviaron campos no permitidos."

    if creacion and "tarifa_diaria" not in datos:
        return None, "La tarifa diaria es obligatoria."

    resultado = {}

    for campo in ("descripcion", "condiciones_convivencia"):
        if campo in datos:
            valor = datos[campo]

            if valor is not None and not isinstance(valor, str):
                return None, f"El campo {campo} debe ser texto."

            if isinstance(valor, str):
                valor = valor.strip() or None

            if valor is not None and len(valor) > 2000:
                return None, f"El campo {campo} es demasiado largo."

            resultado[campo] = valor

    if "capacidad_maxima" in datos:
        capacidad = datos["capacidad_maxima"]

        if (
            isinstance(capacidad, bool)
            or not isinstance(capacidad, int)
            or not 1 <= capacidad <= 20
        ):
            return None, "La capacidad debe estar entre 1 y 20."

        resultado["capacidad_maxima"] = capacidad

    for campo in ("admite_perros", "admite_gatos"):
        if campo in datos:
            if not isinstance(datos[campo], bool):
                return None, f"El campo {campo} debe ser booleano."

            resultado[campo] = datos[campo]

    for campo in ("tarifa_diaria", "tarifa_visita"):
        if campo not in datos:
            continue

        valor = datos[campo]

        if campo == "tarifa_visita" and valor is None:
            resultado[campo] = None
            continue

        precio, mensaje = validar_precio(valor, campo)

        if mensaje:
            return None, mensaje

        resultado[campo] = precio

    perros = resultado.get("admite_perros")
    gatos = resultado.get("admite_gatos")

    if creacion:
        if perros is False and gatos is False:
            return None, "Debes admitir al menos una especie."

    return resultado, None


@cuidadores_bp.get("")
def listar_cuidadores():
    provincia = request.args.get("provincia", "").strip()
    localidad = request.args.get("localidad", "").strip()

    consulta = PerfilCuidador.query.join(
        Usuario,
        PerfilCuidador.usuario_id == Usuario.id
    ).filter(Usuario.activo.is_(True))

    if provincia:
        consulta = consulta.filter(Usuario.provincia == provincia)

    if localidad:
        consulta = consulta.filter(Usuario.localidad == localidad)

    perfiles = consulta.order_by(PerfilCuidador.id.desc()).all()

    return jsonify({
        "cuidadores": [perfil_a_dict(p) for p in perfiles]
    }), 200


@cuidadores_bp.get("/mi-perfil")
@login_required
def obtener_mi_perfil():
    if not es_cuidador():
        return responder_error("Acceso no autorizado.", 403)

    perfil = PerfilCuidador.query.filter_by(
        usuario_id=current_user.id
    ).first()

    if perfil is None:
        return responder_error("Perfil no encontrado.", 404)

    return jsonify({"cuidador": perfil_a_dict(perfil)}), 200


@cuidadores_bp.post("/mi-perfil")
@login_required
def crear_perfil():
    if not es_cuidador():
        return responder_error("Solo un cuidador puede crear perfiles.", 403)

    existente = PerfilCuidador.query.filter_by(
        usuario_id=current_user.id
    ).first()

    if existente is not None:
        return responder_error("Ya tenes un perfil de cuidador.", 409)

    datos = request.get_json(silent=True)
    datos_validos, mensaje = validar_datos(datos, creacion=True)

    if mensaje:
        return responder_error(mensaje)

    perfil = PerfilCuidador(
        usuario_id=current_user.id,
        **datos_validos
    )

    try:
        db.session.add(perfil)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return responder_error("No se pudo crear el perfil.", 409)

    return jsonify({
        "mensaje": "Perfil creado correctamente.",
        "cuidador": perfil_a_dict(perfil)
    }), 201

@cuidadores_bp.put("/mi-perfil")
@login_required
def editar_perfil():
    if not es_cuidador():
        return responder_error("Acceso no autorizado.", 403)

    datos = request.get_json(silent=True)
    datos_validos, mensaje = validar_datos(datos)

    if mensaje:
        return responder_error(mensaje)

    # Bloquear el perfil antes de verificar o modificar.
    perfil = PerfilCuidador.query.filter_by(
        usuario_id=current_user.id
    ).with_for_update().first()

    if perfil is None:
        db.session.rollback()
        return responder_error("Perfil no encontrado.", 404)

    admite_perros = datos_validos.get(
        "admite_perros", perfil.admite_perros
    )
    admite_gatos = datos_validos.get(
        "admite_gatos", perfil.admite_gatos
    )

    if not admite_perros and not admite_gatos:
        db.session.rollback()
        return responder_error(
            "Debes admitir al menos una especie."
        )

    nueva_capacidad = datos_validos.get(
        "capacidad_maxima",
        perfil.capacidad_maxima
    )

    # Una reduccion no puede dejar reservas sin cupos.
    if nueva_capacidad < perfil.capacidad_maxima:
        if not capacidad_suficiente(
            perfil.id, nueva_capacidad
        ):
            db.session.rollback()
            return responder_error(
                "No podes reducir la capacidad porque "
                "existen reservas aceptadas.",
                409
            )

    # Tampoco se puede dejar de admitir una especie
    # que ya tiene reservas futuras comprometidas.
    cambia_especies = (
        admite_perros != perfil.admite_perros
        or admite_gatos != perfil.admite_gatos
    )

    if cambia_especies:
        reservas = reservas_comprometidas(perfil.id)

        for reserva in reservas:
            for mascota in reserva.mascotas_asociadas:
                if (
                    mascota.especie_snapshot == "PERRO"
                    and not admite_perros
                ):
                    db.session.rollback()
                    return responder_error(
                        "Hay reservas aceptadas con perros.",
                        409
                    )

                if (
                    mascota.especie_snapshot == "GATO"
                    and not admite_gatos
                ):
                    db.session.rollback()
                    return responder_error(
                        "Hay reservas aceptadas con gatos.",
                        409
                    )

    for campo, valor in datos_validos.items():
        setattr(perfil, campo, valor)

    db.session.commit()

    return jsonify({
        "mensaje": "Perfil actualizado correctamente.",
        "cuidador": perfil_a_dict(perfil)
    }), 200


@cuidadores_bp.get("/<int:cuidador_id>")
def obtener_cuidador(cuidador_id):
    perfil = PerfilCuidador.query.join(
        Usuario,
        PerfilCuidador.usuario_id == Usuario.id
    ).filter(
        PerfilCuidador.id == cuidador_id,
        Usuario.activo.is_(True)
    ).first()

    if perfil is None:
        return responder_error("Cuidador no encontrado.", 404)

    return jsonify({"cuidador": perfil_a_dict(perfil)}), 200

@cuidadores_bp.get("/<int:cuidador_id>/disponibilidades")
def disponibilidades_publicas(cuidador_id):
    perfil = PerfilCuidador.query.join(
        Usuario,
        PerfilCuidador.usuario_id == Usuario.id
    ).filter(
        PerfilCuidador.id == cuidador_id,
        Usuario.activo.is_(True)
    ).first()

    if perfil is None:
        return responder_error("Cuidador no encontrado.", 404)

    registros = Disponibilidad.query.filter_by(
        cuidador_id=perfil.id,
        activo=True
    ).order_by(
        Disponibilidad.fecha_desde,
        Disponibilidad.hora_desde
    ).all()

    return jsonify({
        "cuidador_id": perfil.id,
        "disponibilidades": [
            disponibilidad_a_dict(d) for d in registros
        ]
    }), 200