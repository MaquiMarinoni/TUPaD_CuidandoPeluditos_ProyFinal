
from flask import Blueprint, jsonify, request
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_wtf.csrf import generate_csrf
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.exc import IntegrityError

from backend.app.extensions import db
from backend.app.models import Usuario, Rol


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def datos_usuario(usuario):
    """Datos públicos de la sesión, sin contraseña."""
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "email": usuario.email,
        "telefono": usuario.telefono,
        "provincia": usuario.provincia,
        "localidad": usuario.localidad,
        "rol": usuario.rol.nombre,
    }


def error(mensaje, codigo):
    return jsonify({"error": mensaje}), codigo


@auth_bp.get("/csrf-token")
def csrf_token():
    return jsonify({"csrf_token": generate_csrf()}), 200


@auth_bp.post("/register")
def register():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return error("Se requieren datos JSON válidos.", 400)

    campos = [
        "nombre", "apellido", "email", "password",
        "telefono", "provincia", "localidad", "rol"
    ]

    if any(
        not isinstance(datos.get(campo), str)
        or not datos[campo].strip()
        for campo in campos
    ):
        return error("Completá todos los campos obligatorios.", 400)

    rol_nombre = datos["rol"].strip().upper()

    if rol_nombre not in ("DUENO", "CUIDADOR"):
        return error("El rol seleccionado no es válido.", 400)

    try:
        email = validate_email(
            datos["email"].strip(),
            check_deliverability=False
        ).normalized.lower()
    except EmailNotValidError:
        return error("El correo electrónico no es válido.", 400)

    if len(datos["password"]) < 8:
        return error("La contraseña debe tener al menos 8 caracteres.", 400)

    longitudes = {
        "nombre": 60,
        "apellido": 60,
        "telefono": 30,
        "provincia": 60,
        "localidad": 60,
    }

    for campo, maximo in longitudes.items():
        if len(datos[campo].strip()) > maximo:
            return error(f"El campo {campo} es demasiado largo.", 400)

    direccion = datos.get("direccion")

    if direccion is not None:
        if not isinstance(direccion, str):
            return error("La dirección no es válida.", 400)

        direccion = direccion.strip() or None

        if direccion and len(direccion) > 120:
            return error("La dirección es demasiado larga.", 400)

    if Usuario.query.filter_by(email=email).first():
        return error("Ya existe una cuenta con ese correo.", 409)

    rol = Rol.query.filter_by(nombre=rol_nombre).first()

    if rol is None:
        return error("El rol no está configurado en la base de datos.", 500)

    usuario = Usuario(
        nombre=datos["nombre"].strip(),
        apellido=datos["apellido"].strip(),
        email=email,
        telefono=datos["telefono"].strip(),
        provincia=datos["provincia"].strip(),
        localidad=datos["localidad"].strip(),
        direccion=direccion,
        rol_id=rol.id,
    )

    usuario.set_password(datos["password"])

    try:
        db.session.add(usuario)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("No se pudo registrar la cuenta. Verificá el correo.", 409)

    return jsonify({
        "mensaje": "Usuario registrado correctamente.",
        "usuario": datos_usuario(usuario),
    }), 201


@auth_bp.post("/login")
def login():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return error("Se requieren datos JSON válidos.", 400)

    email = datos.get("email")
    password = datos.get("password")

    if not isinstance(email, str) or not isinstance(password, str):
        return error("Ingresá correo y contraseña.", 400)

    usuario = Usuario.query.filter_by(
        email=email.strip().lower()
    ).first()

    if (
        usuario is None
        or not usuario.activo
        or not usuario.check_password(password)
    ):
        return error("Correo o contraseña incorrectos.", 401)

    login_user(usuario)

    return jsonify({
        "mensaje": "Sesión iniciada correctamente.",
        "usuario": datos_usuario(usuario),
    }), 200


@auth_bp.get("/me")
def me():
    if not current_user.is_authenticated or not current_user.activo:
        return jsonify({"autenticado": False, "usuario": None}), 200

    return jsonify({
        "autenticado": True,
        "usuario": datos_usuario(current_user),
    }), 200


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"mensaje": "Sesión cerrada correctamente."}), 200
