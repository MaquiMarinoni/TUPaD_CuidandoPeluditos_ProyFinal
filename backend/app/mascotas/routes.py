
from datetime import date

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from backend.app.extensions import db
from backend.app.models import Mascota


mascotas_bp = Blueprint(
    "mascotas",
    __name__,
    url_prefix="/api/mascotas"
)

ESPECIES = {"PERRO", "GATO"}
TAMANOS = {"CHICO", "MEDIANO", "GRANDE"}

CAMPOS_PERMITIDOS = {
    "nombre",
    "especie",
    "raza",
    "tamano",
    "fecha_nacimiento",
    "cuidados_especiales",
    "contacto_veterinario",
}


def responder_error(mensaje, codigo=400):
    return jsonify({"error": mensaje}), codigo


def verificar_dueno():
    """Comprueba que el usuario pueda gestionar mascotas."""
    return current_user.activo and current_user.es_dueno()


def mascota_a_dict(mascota):
    """Convierte una mascota en datos JSON."""
    return {
        "id": mascota.id,
        "nombre": mascota.nombre,
        "especie": mascota.especie,
        "raza": mascota.raza,
        "tamano": mascota.tamano,
        "fecha_nacimiento": (
            mascota.fecha_nacimiento.isoformat()
            if mascota.fecha_nacimiento else None
        ),
        "cuidados_especiales": mascota.cuidados_especiales,
        "contacto_veterinario": mascota.contacto_veterinario,
        "activo": mascota.activo,
    }


def buscar_mascota(mascota_id):
    """Busca una mascota activa del dueño autenticado."""
    return Mascota.query.filter_by(
        id=mascota_id,
        dueno_id=current_user.id,
        activo=True
    ).first()


def validar_datos(datos, parcial=False):
    """
    Valida los datos recibidos.

    parcial=False: todos los campos obligatorios.
    parcial=True: permite editar solamente algunos campos.
    """
    if not isinstance(datos, dict):
        return None, "Se requieren datos JSON válidos."

    if not parcial:
        for campo in ("nombre", "especie", "tamano"):
            if campo not in datos:
                return None, f"El campo {campo} es obligatorio."

    if parcial and not datos:
        return None, "No se enviaron campos para modificar."

    desconocidos = set(datos) - CAMPOS_PERMITIDOS

    if desconocidos:
        return None, "Se enviaron campos no permitidos."

    resultado = {}

    longitudes = {
        "nombre": 50,
        "raza": 50,
        "contacto_veterinario": 100,
    }

    campos_obligatorios = {
        "nombre", "especie", "tamano"
    }

    campos_texto = {
        "nombre",
        "especie",
        "raza",
        "tamano",
        "cuidados_especiales",
        "contacto_veterinario",
    }

    for campo in campos_texto:
        if campo not in datos:
            continue

        valor = datos[campo]

        if campo in campos_obligatorios:
            if not isinstance(valor, str) or not valor.strip():
                return None, f"El campo {campo} es obligatorio."
        elif valor is not None and not isinstance(valor, str):
            return None, f"El campo {campo} debe ser texto."

        if isinstance(valor, str):
            valor = valor.strip() or None

        if campo in longitudes:
            if valor is not None and len(valor) > longitudes[campo]:
                return None, f"El campo {campo} es demasiado largo."

        if campo in ("especie", "tamano"):
            valor = valor.upper()

        resultado[campo] = valor

    if "especie" in resultado:
        if resultado["especie"] not in ESPECIES:
            return None, "La especie debe ser PERRO o GATO."

    if "tamano" in resultado:
        if resultado["tamano"] not in TAMANOS:
            return None, "El tamaño indicado no es válido."

    if "fecha_nacimiento" in datos:
        valor = datos["fecha_nacimiento"]

        if valor is None or valor == "":
            resultado["fecha_nacimiento"] = None
        elif isinstance(valor, str):
            try:
                fecha = date.fromisoformat(valor)

                if fecha > date.today():
                    return None, "La fecha no puede ser futura."

                resultado["fecha_nacimiento"] = fecha
            except ValueError:
                return None, "La fecha debe tener formato AAAA-MM-DD."
        else:
            return None, "La fecha de nacimiento no es válida."

    return resultado, None


@mascotas_bp.get("")
@login_required
def listar_mascotas():
    if not verificar_dueno():
        return responder_error("Acceso no autorizado.", 403)

    mascotas = Mascota.query.filter_by(
        dueno_id=current_user.id,
        activo=True
    ).order_by(Mascota.id.desc()).all()

    return jsonify({
        "mascotas": [mascota_a_dict(m) for m in mascotas]
    }), 200


@mascotas_bp.get("/<int:mascota_id>")
@login_required
def obtener_mascota(mascota_id):
    if not verificar_dueno():
        return responder_error("Acceso no autorizado.", 403)

    mascota = buscar_mascota(mascota_id)

    if mascota is None:
        return responder_error("Mascota no encontrada.", 404)

    return jsonify({"mascota": mascota_a_dict(mascota)}), 200


@mascotas_bp.post("")
@login_required
def crear_mascota():
    if not verificar_dueno():
        return responder_error("Acceso no autorizado.", 403)

    datos = request.get_json(silent=True)
    datos_validos, error = validar_datos(datos)

    if error:
        return responder_error(error)

    mascota = Mascota(
        dueno_id=current_user.id,
        **datos_validos
    )

    db.session.add(mascota)
    db.session.commit()

    return jsonify({
        "mensaje": "Mascota registrada correctamente.",
        "mascota": mascota_a_dict(mascota)
    }), 201


@mascotas_bp.put("/<int:mascota_id>")
@login_required
def editar_mascota(mascota_id):
    if not verificar_dueno():
        return responder_error("Acceso no autorizado.", 403)

    mascota = buscar_mascota(mascota_id)

    if mascota is None:
        return responder_error("Mascota no encontrada.", 404)

    datos = request.get_json(silent=True)
    datos_validos, error = validar_datos(datos, parcial=True)

    if error:
        return responder_error(error)

    for campo, valor in datos_validos.items():
        setattr(mascota, campo, valor)

    db.session.commit()

    return jsonify({
        "mensaje": "Mascota actualizada correctamente.",
        "mascota": mascota_a_dict(mascota)
    }), 200


@mascotas_bp.delete("/<int:mascota_id>")
@login_required
def eliminar_mascota(mascota_id):
    if not verificar_dueno():
        return responder_error("Acceso no autorizado.", 403)

    mascota = buscar_mascota(mascota_id)

    if mascota is None:
        return responder_error("Mascota no encontrada.", 404)

    mascota.activo = False
    db.session.commit()

    return jsonify({
        "mensaje": "Mascota desactivada correctamente."
    }), 200
