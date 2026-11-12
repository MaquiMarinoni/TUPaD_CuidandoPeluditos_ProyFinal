
import os

from flask import Flask, app, jsonify
from flask_wtf.csrf import CSRFError

from .config import config_by_name
from .extensions import db, login_manager, migrate, csrf


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "dev")

    app = Flask(__name__)

    app.config.from_object(config_by_name[config_name])

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = config_name == "prod"

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Cargar los modelos antes de registrar las rutas.
    from . import models

    # Registrar el módulo de autenticación.
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .mascotas import mascotas_bp
    app.register_blueprint(mascotas_bp)

    from .cuidadores import cuidadores_bp
    app.register_blueprint(cuidadores_bp)

    from .disponibilidades import disponibilidades_bp
    app.register_blueprint(disponibilidades_bp)

    from .solicitudes import solicitudes_bp
    app.register_blueprint(solicitudes_bp)

    from .visitas import visitas_bp
    app.register_blueprint(visitas_bp)

    from .incidencias import incidencias_bp
    app.register_blueprint(incidencias_bp)
    from .valoraciones import valoraciones_bp
    app.register_blueprint(valoraciones_bp)

    @app.route("/health")
    def health_check():
        return {
            "status": "ok",
            "app": "Cuidando Peluditos API/Web"
        }, 200

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({
            "error": "Debés iniciar sesión para continuar."
        }), 401

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return jsonify({
            "error": "Token de seguridad inválido o ausente."
        }), 400

    return app
