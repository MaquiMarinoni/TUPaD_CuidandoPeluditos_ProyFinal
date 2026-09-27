import os
from flask import Flask
from .config import config_by_name
from .extensions import db, login_manager, migrate

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'dev')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Asegurar que exista la carpeta instance para SQLite local
    os.makedirs(app.instance_path, exist_ok=True)

    # Inicialización de extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Registro de Blueprints (se irán activando a medida que los creemos)
    # from app.modules.auth.routes import auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/auth')

    @app.route('/health')
    def health_check():
        return {'status': 'ok', 'app': 'Cuidando Peluditos API/Web'}, 200

    # Registrar modelos
    from . import models
    return app