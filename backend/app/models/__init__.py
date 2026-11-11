
from backend.app.extensions import login_manager

from .usuario import Usuario, Rol
from .perfil_cuidador import PerfilCuidador, Disponibilidad
from .mascota import Mascota
from .solicitud import Solicitud, SolicitudMascota
from .valoracion import Valoracion
from .incidencia import Incidencia
from .historial_estado import HistorialEstado


@login_manager.user_loader
def load_user(user_id):
    return db_get_usuario(user_id)


def db_get_usuario(user_id):
    try:
        return Usuario.query.get(int(user_id))
    except (ValueError, TypeError):
        return None
