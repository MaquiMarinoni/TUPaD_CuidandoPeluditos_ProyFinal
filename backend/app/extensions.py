from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

# Configuración de redirección ante accesos no autorizados
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Iniciá sesión para acceder a esta sección.'
login_manager.login_message_category = 'warning'