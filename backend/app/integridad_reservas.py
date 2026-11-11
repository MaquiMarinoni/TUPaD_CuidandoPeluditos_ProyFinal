
from datetime import date, timedelta

from sqlalchemy import select

from backend.app.extensions import db
from backend.app.models import Solicitud


ESTADOS_RESERVADOS = ("ACEPTADA", "FINALIZADA")


def reservas_comprometidas(perfil_id):
    """
    Busca alojamientos aceptados que todavia
    tienen noches futuras comprometidas.

    Las reservas finalizadas no deberian tener
    noches futuras, pero se consideran por seguridad.
    """
    return db.session.execute(
        select(Solicitud).where(
            Solicitud.cuidador_id == perfil_id,
            Solicitud.modalidad == "ALOJAMIENTO",
            Solicitud.estado.in_(ESTADOS_RESERVADOS),
            Solicitud.fecha_hasta > date.today(),
        ).with_for_update()
    ).scalars().all()


def capacidad_suficiente(perfil_id, nueva_capacidad):
    """
    Comprueba la cantidad total de mascotas
    que ocupan cada noche futura.

    Usa eventos de ingreso (+mascotas) y salida
    (-mascotas) para calcular la ocupacion maxima.
    """
    reservas = reservas_comprometidas(perfil_id)
    eventos = {}

    for reserva in reservas:
        ingreso = max(reserva.fecha_desde, date.today())
        salida = reserva.fecha_hasta

        eventos[ingreso] = (
            eventos.get(ingreso, 0) + reserva.total_mascotas
        )

        eventos[salida] = (
            eventos.get(salida, 0) - reserva.total_mascotas
        )

    ocupacion = 0

    for fecha in sorted(eventos):
        ocupacion += eventos[fecha]

        if ocupacion > nueva_capacidad:
            return False

    return True


def afecta_reserva_aceptada(disponibilidad):
    """
    Impide alterar una franja de alojamiento
    que se superpone con reservas ya aceptadas.

    Es una regla conservadora: mientras haya una
    reserva comprometida, no se altera esa franja.
    """
    if disponibilidad.modalidad != "ALOJAMIENTO":
        return False

    for reserva in reservas_comprometidas(
        disponibilidad.cuidador_id
    ):
        if (
            reserva.fecha_desde < disponibilidad.fecha_hasta
            and reserva.fecha_hasta > disponibilidad.fecha_desde
        ):
            return True

    return False

