
from datetime import date, datetime

from sqlalchemy import select

from backend.app.extensions import db
from backend.app.models import Disponibilidad, Solicitud, SolicitudMascota


def fecha_visita(valor):
    if not isinstance(valor, str):
        raise ValueError("La fecha debe tener formato AAAA-MM-DD.")

    try:
        fecha = date.fromisoformat(valor)
    except ValueError:
        raise ValueError("La fecha no es valida.")

    if fecha.isoformat() != valor:
        raise ValueError("La fecha debe tener formato AAAA-MM-DD.")

    return fecha


def hora_visita(valor):
    if not isinstance(valor, str):
        raise ValueError("La hora debe tener formato HH:MM.")

    try:
        hora = datetime.strptime(valor, "%H:%M").time()
    except ValueError:
        raise ValueError("La hora no es valida.")

    if hora.strftime("%H:%M") != valor:
        raise ValueError("La hora debe tener formato HH:MM.")

    return hora


def horario_cubierto(perfil_id, fecha, inicio, fin):
    """Comprueba que exista una franja que cubra el turno completo."""
    return db.session.execute(
        select(Disponibilidad.id).where(
            Disponibilidad.cuidador_id == perfil_id,
            Disponibilidad.modalidad == "VISITA",
            Disponibilidad.activo.is_(True),
            Disponibilidad.fecha_desde <= fecha,
            Disponibilidad.fecha_hasta >= fecha,
            Disponibilidad.hora_desde <= inicio,
            Disponibilidad.hora_hasta >= fin,
        )
    ).first() is not None


def turnos_superpuestos(perfil_id, fecha, inicio, fin):
    """Un cuidador solo puede atender una visita por turno."""
    return db.session.execute(
        select(Solicitud.id).where(
            Solicitud.cuidador_id == perfil_id,
            Solicitud.modalidad == "VISITA",
            Solicitud.estado.in_(("ACEPTADA", "FINALIZADA")),
            Solicitud.fecha_desde == fecha,
            Solicitud.hora_desde < fin,
            Solicitud.hora_hasta > inicio,
        ).with_for_update()
    ).first() is not None


def conflicto_mascotas_visita(ids, fecha, inicio, fin):
    """
    Una mascota no puede tener:
    - otra visita aceptada con horarios superpuestos;
    - un alojamiento aceptado que incluya esa fecha.
    """
    consulta = (
        select(Solicitud)
        .join(
            SolicitudMascota,
            SolicitudMascota.solicitud_id == Solicitud.id
        )
        .where(
            SolicitudMascota.mascota_id.in_(ids),
            Solicitud.estado.in_(("ACEPTADA", "FINALIZADA")),
        )
        .with_for_update()
    )

    for reserva in db.session.execute(consulta).scalars().unique():
        if reserva.modalidad == "ALOJAMIENTO":
            if reserva.fecha_desde <= fecha < reserva.fecha_hasta:
                return True

        elif reserva.modalidad == "VISITA":
            if (
                reserva.fecha_desde == fecha
                and reserva.hora_desde < fin
                and reserva.hora_hasta > inicio
            ):
                return True

    return False


def conflicto_mascotas_alojamiento(ids, ingreso, salida):
    """Impide alojamiento que coincida con visitas ya aceptadas."""
    consulta = (
        select(Solicitud)
        .join(
            SolicitudMascota,
            SolicitudMascota.solicitud_id == Solicitud.id
        )
        .where(
            SolicitudMascota.mascota_id.in_(ids),
            Solicitud.modalidad == "VISITA",
            Solicitud.estado.in_(("ACEPTADA", "FINALIZADA")),
            Solicitud.fecha_desde >= ingreso,
            Solicitud.fecha_desde < salida,
        )
        .with_for_update()
    )

    return db.session.execute(consulta).first() is not None
