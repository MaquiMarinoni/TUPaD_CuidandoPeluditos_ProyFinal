
from datetime import date, datetime, timedelta
from decimal import Decimal

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError

from backend.app.extensions import db
from backend.app.models import (
    Disponibilidad,
    HistorialEstado,
    Mascota,
    PerfilCuidador,
    Solicitud,
    SolicitudMascota,
)


solicitudes_bp = Blueprint(
    "solicitudes",
    __name__,
    url_prefix="/api/solicitudes"
)

ESTADOS_QUE_OCUPAN = ("ACEPTADA", "FINALIZADA")

CAMPOS_CREACION = {
    "cuidador_id",
    "modalidad",
    "fecha_desde",
    "fecha_hasta",
    "mascotas_ids",
    "contacto_emergencia",
    "veterinario_emergencia",
    "autorizacion_urgencia",
    "limite_gastos_urgencia",
}


def error(mensaje, codigo=400):
    return jsonify({"error": mensaje}), codigo


def fecha_valida(valor):
    if not isinstance(valor, str):
        raise ValueError(
            "Las fechas deben ser texto AAAA-MM-DD."
        )

    try:
        fecha = date.fromisoformat(valor)
    except ValueError:
        raise ValueError("Formato de fecha incorrecto.")

    if fecha.isoformat() != valor:
        raise ValueError("Formato de fecha incorrecto.")

    return fecha


def dinero(valor):
    if isinstance(valor, bool) or not isinstance(
        valor, (str, int, float)
    ):
        raise ValueError("El limite de gastos no es valido.")

    try:
        resultado = Decimal(str(valor))
    except Exception:
        raise ValueError("El limite de gastos no es valido.")

    if (
        not resultado.is_finite()
        or resultado <= 0
        or resultado > Decimal("99999999.99")
        or resultado != resultado.quantize(Decimal("0.01"))
    ):
        raise ValueError(
            "El limite de gastos debe ser positivo."
        )

    return resultado


def validar_creacion(datos):
    """
    Valida las solicitudes de alojamiento.

    Las visitas se crean mediante POST /api/visitas.
    """
    if not isinstance(datos, dict):
        raise ValueError("Se requieren datos JSON.")

    if set(datos) - CAMPOS_CREACION:
        raise ValueError("Se enviaron campos no permitidos.")

    if datos.get("modalidad") != "ALOJAMIENTO":
        raise ValueError(
            "Para visitas utiliza POST /api/visitas."
        )

    cuidador_id = datos.get("cuidador_id")

    if type(cuidador_id) is not int or cuidador_id <= 0:
        raise ValueError("El cuidador_id no es valido.")

    inicio = fecha_valida(datos.get("fecha_desde"))
    salida = fecha_valida(datos.get("fecha_hasta"))

    if inicio < date.today():
        raise ValueError(
            "El ingreso no puede estar en el pasado."
        )

    noches = (salida - inicio).days

    if noches < 1 or noches > 365:
        raise ValueError(
            "La estadia debe ser de 1 a 365 noches."
        )

    ids = datos.get("mascotas_ids")

    if (
        not isinstance(ids, list)
        or not ids
        or len(ids) > 20
    ):
        raise ValueError(
            "Selecciona entre 1 y 20 mascotas."
        )

    if any(
        type(i) is not int or i <= 0
        for i in ids
    ):
        raise ValueError(
            "Los IDs de mascotas no son validos."
        )

    if len(ids) != len(set(ids)):
        raise ValueError(
            "No se pueden repetir mascotas."
        )

    contacto = datos.get("contacto_emergencia")

    if (
        not isinstance(contacto, str)
        or not contacto.strip()
        or len(contacto.strip()) > 100
    ):
        raise ValueError(
            "El contacto de emergencia es obligatorio."
        )

    autorizacion = datos.get("autorizacion_urgencia")

    if type(autorizacion) is not bool:
        raise ValueError(
            "Debes indicar la autorizacion de urgencia."
        )

    veterinario = datos.get("veterinario_emergencia")

    if veterinario is not None:
        if not isinstance(veterinario, str):
            raise ValueError(
                "El veterinario no es valido."
            )

        veterinario = veterinario.strip() or None

        if veterinario and len(veterinario) > 100:
            raise ValueError(
                "El veterinario es demasiado largo."
            )

    limite = datos.get("limite_gastos_urgencia")

    if autorizacion:
        if not veterinario or limite is None:
            raise ValueError(
                "Para autorizar urgencias indica "
                "veterinario y limite de gastos."
            )

        limite = dinero(limite)

    elif limite is not None:
        raise ValueError(
            "No indiques limite de gastos "
            "sin autorizacion."
        )

    return {
        "cuidador_id": cuidador_id,
        "fecha_desde": inicio,
        "fecha_hasta": salida,
        "noches": noches,
        "mascotas_ids": ids,
        "contacto_emergencia": contacto.strip(),
        "veterinario_emergencia": veterinario,
        "autorizacion_urgencia": autorizacion,
        "limite_gastos_urgencia": limite,
    }


def cubre_alojamiento(perfil_id, inicio, salida):
    """
    Verifica que exista una disponibilidad activa
    que cubra todas las noches solicitadas.
    """
    consulta = select(Disponibilidad.id).where(
        Disponibilidad.cuidador_id == perfil_id,
        Disponibilidad.modalidad == "ALOJAMIENTO",
        Disponibilidad.activo.is_(True),
        Disponibilidad.fecha_desde <= inicio,
        Disponibilidad.fecha_hasta >= salida,
    )

    return db.session.execute(consulta).first() is not None


def reservas_que_ocupan(perfil_id, inicio, salida):
    """
    Busca reservas que ocupan plazas.

    Se utiliza dentro de una transaccion
    despues de bloquear el perfil del cuidador.
    """
    consulta = (
        select(Solicitud)
        .where(
            Solicitud.cuidador_id == perfil_id,
            Solicitud.modalidad == "ALOJAMIENTO",
            Solicitud.estado.in_(ESTADOS_QUE_OCUPAN),
            Solicitud.fecha_desde < salida,
            Solicitud.fecha_hasta > inicio,
        )
        .with_for_update()
    )

    return db.session.execute(
        consulta
    ).scalars().all()


def hay_cupo(perfil, inicio, salida, cantidad, reservas):
    """
    Calcula la ocupacion noche por noche.

    La fecha de salida no consume una noche.
    """
    if cantidad > perfil.capacidad_maxima:
        return False

    fecha = inicio

    while fecha < salida:
        ocupadas = sum(
            reserva.total_mascotas
            for reserva in reservas
            if (
                reserva.fecha_desde <= fecha
                < reserva.fecha_hasta
            )
        )

        if ocupadas + cantidad > perfil.capacidad_maxima:
            return False

        fecha += timedelta(days=1)

    return True


def mascota_ya_reservada(ids, inicio, salida):
    """
    Evita alojamientos simultaneos
    para una misma mascota.
    """
    consulta = (
        select(SolicitudMascota.mascota_id)
        .join(
            Solicitud,
            SolicitudMascota.solicitud_id
            == Solicitud.id,
        )
        .where(
            SolicitudMascota.mascota_id.in_(ids),
            Solicitud.modalidad == "ALOJAMIENTO",
            Solicitud.estado.in_(ESTADOS_QUE_OCUPAN),
            Solicitud.fecha_desde < salida,
            Solicitud.fecha_hasta > inicio,
        )
        .with_for_update()
    )

    return db.session.execute(
        consulta
    ).first() is not None


def bloquear_mascotas(ids):
    """
    Bloquea las filas de las mascotas en orden
    para prevenir reservas simultaneas incompatibles.
    """
    consulta = (
        select(Mascota)
        .where(Mascota.id.in_(ids))
        .order_by(Mascota.id)
        .with_for_update()
    )

    return db.session.execute(
        consulta
    ).scalars().all()


def registrar_estado(solicitud, anterior, nuevo, motivo=None):
    """
    Guarda el cambio de estado y su responsable.
    """
    historial = HistorialEstado(
        solicitud=solicitud,
        usuario_id=current_user.id,
        estado_anterior=anterior,
        estado_nuevo=nuevo,
        motivo=motivo,
    )

    db.session.add(historial)


def solicitud_a_dict(solicitud):
    """
    Convierte una solicitud en JSON.

    Sirve tanto para alojamiento como para visitas.
    """
    # Los datos de contacto y cuidados detallados son privados.
    # El dueno los ve siempre; el cuidador solo al aceptar el servicio.
    mostrar_privados = (
        current_user.is_authenticated
        and current_user.activo
        and (
            current_user.id == solicitud.dueno_id
            or (
                solicitud.estado in ("ACEPTADA", "FINALIZADA")
                and current_user.es_cuidador()
                and solicitud.cuidador_perfil.usuario_id == current_user.id
            )
        )
    )

    return {
        "id": solicitud.id,
        "dueno_id": solicitud.dueno_id,
        "cuidador_id": solicitud.cuidador_id,
        "modalidad": solicitud.modalidad,
        "fecha_desde": solicitud.fecha_desde.isoformat(),
        "fecha_hasta": solicitud.fecha_hasta.isoformat(),

        "hora_desde": (
            solicitud.hora_desde.strftime("%H:%M")
            if solicitud.hora_desde
            else None
        ),

        "hora_hasta": (
            solicitud.hora_hasta.strftime("%H:%M")
            if solicitud.hora_hasta
            else None
        ),

        "direccion_servicio": (solicitud.direccion_servicio if mostrar_privados else None),

        "noches": (
            (solicitud.fecha_hasta - solicitud.fecha_desde).days
            if solicitud.modalidad == "ALOJAMIENTO"
            else None
        ),

        "estado": solicitud.estado,
        "total_mascotas": solicitud.total_mascotas,

        "monto_total": (
            str(solicitud.monto_total)
            if solicitud.monto_total is not None
            else None
        ),

        "contacto_emergencia": (solicitud.contacto_emergencia if mostrar_privados else None),
        "veterinario_emergencia": (solicitud.veterinario_emergencia if mostrar_privados else None),
        "autorizacion_urgencia": solicitud.autorizacion_urgencia,

        "limite_gastos_urgencia": (
            str(solicitud.limite_gastos_urgencia)
            if mostrar_privados and solicitud.limite_gastos_urgencia is not None
            else None
        ),

        "mascotas": [
            {
                "id": item.mascota_id,
                "nombre": item.nombre_snapshot,
                "especie": item.especie_snapshot,
                "cuidados_especiales": (item.cuidados_snapshot if mostrar_privados else None),
                "contacto_veterinario": (item.veterinario_snapshot if mostrar_privados else None),
            }
            for item in solicitud.mascotas_asociadas
        ],

        "historial": [
            {
                "estado_anterior": h.estado_anterior,
                "estado_nuevo": h.estado_nuevo,
                "usuario_id": h.usuario_id,
                "motivo": h.motivo,
                "fecha_cambio": h.fecha_cambio.isoformat(),
            }
            for h in solicitud.historial_estados
        ],
    }


def puede_ver(solicitud):
    """
    Solo el dueño y el cuidador destinatario
    pueden consultar una solicitud.
    """
    if not current_user.activo:
        return False

    if current_user.id == solicitud.dueno_id:
        return True

    return (
        current_user.es_cuidador()
        and solicitud.cuidador_perfil.usuario_id
        == current_user.id
    )


@solicitudes_bp.post("")
@login_required
def crear_solicitud():
    """
    Crea una solicitud de alojamiento pendiente.

    Las solicitudes de visitas se crean
    mediante POST /api/visitas.
    """
    if (
        not current_user.activo
        or not current_user.es_dueno()
    ):
        return error(
            "Solo un dueño puede crear solicitudes.",
            403,
        )

    try:
        datos = validar_creacion(
            request.get_json(silent=True)
        )
    except ValueError as exc:
        return error(str(exc))

    try:
        perfil = db.session.execute(
            select(PerfilCuidador)
            .where(
                PerfilCuidador.id
                == datos["cuidador_id"]
            )
            .with_for_update()
        ).scalar_one_or_none()

        if perfil is None or not perfil.usuario.activo:
            db.session.rollback()
            return error(
                "Cuidador no encontrado.",
                404,
            )

        if not cubre_alojamiento(
            perfil.id,
            datos["fecha_desde"],
            datos["fecha_hasta"],
        ):
            db.session.rollback()
            return error(
                "El cuidador no ofrece esas fechas.",
                409,
            )

        mascotas = db.session.execute(
            select(Mascota).where(
                Mascota.id.in_(datos["mascotas_ids"]),
                Mascota.dueno_id == current_user.id,
                Mascota.activo.is_(True),
            )
        ).scalars().all()

        if len(mascotas) != len(datos["mascotas_ids"]):
            db.session.rollback()
            return error(
                "Alguna mascota no te pertenece "
                "o no esta activa.",
                403,
            )

        for mascota in mascotas:
            if (
                mascota.especie == "PERRO"
                and not perfil.admite_perros
            ):
                db.session.rollback()
                return error(
                    "Este cuidador no admite perros."
                )

            if (
                mascota.especie == "GATO"
                and not perfil.admite_gatos
            ):
                db.session.rollback()
                return error(
                    "Este cuidador no admite gatos."
                )

        # Bloqueo comun para reservas de una misma mascota.
        bloquear_mascotas(datos["mascotas_ids"])

        reservas = reservas_que_ocupan(
            perfil.id,
            datos["fecha_desde"],
            datos["fecha_hasta"],
        )

        if not hay_cupo(
            perfil,
            datos["fecha_desde"],
            datos["fecha_hasta"],
            len(mascotas),
            reservas,
        ):
            db.session.rollback()
            return error(
                "No hay cupos para todas las noches.",
                409,
            )

        if mascota_ya_reservada(
            datos["mascotas_ids"],
            datos["fecha_desde"],
            datos["fecha_hasta"],
        ):
            db.session.rollback()
            return error(
                "Una mascota ya tiene "
                "una reserva aceptada.",
                409,
            )

        # Evitar alojamiento durante visitas aceptadas.
        from backend.app.visitas.logica import (
            conflicto_mascotas_alojamiento,
        )

        if conflicto_mascotas_alojamiento(
            datos["mascotas_ids"],
            datos["fecha_desde"],
            datos["fecha_hasta"],
        ):
            db.session.rollback()
            return error(
                "Una mascota tiene una visita aceptada "
                "durante la estadia.",
                409,
            )

        monto = (
            perfil.tarifa_diaria
            * Decimal(len(mascotas))
            * Decimal(datos["noches"])
        )

        if monto > Decimal("99999999.99"):
            db.session.rollback()
            return error(
                "El monto supera el maximo permitido."
            )

        solicitud = Solicitud(
            dueno_id=current_user.id,
            cuidador_id=perfil.id,
            modalidad="ALOJAMIENTO",
            fecha_desde=datos["fecha_desde"],
            fecha_hasta=datos["fecha_hasta"],
            estado="PENDIENTE",
            total_mascotas=len(mascotas),
            monto_total=monto,
            contacto_emergencia=datos["contacto_emergencia"],
            veterinario_emergencia=datos["veterinario_emergencia"],
            autorizacion_urgencia=datos["autorizacion_urgencia"],
            limite_gastos_urgencia=datos["limite_gastos_urgencia"],
        )

        for mascota in mascotas:
            solicitud.mascotas_asociadas.append(
                SolicitudMascota(
                    mascota_id=mascota.id,
                    nombre_snapshot=mascota.nombre,
                    especie_snapshot=mascota.especie,
                    cuidados_snapshot=mascota.cuidados_especiales,
                    veterinario_snapshot=mascota.contacto_veterinario,
                )
            )

        registrar_estado(
            solicitud,
            None,
            "PENDIENTE",
        )

        db.session.add(solicitud)
        db.session.commit()

        return jsonify({
            "mensaje": "Solicitud creada correctamente.",
            "solicitud": solicitud_a_dict(solicitud),
        }), 201

    except (IntegrityError, OperationalError):
        db.session.rollback()
        return error(
            "No se pudo registrar la solicitud.",
            409,
        )


@solicitudes_bp.get("")
@login_required
def listar_solicitudes():
    """
    Dueño: solicitudes que creo.
    Cuidador: solicitudes que recibio.
    """
    if not current_user.activo:
        return error(
            "Acceso no autorizado.",
            403,
        )

    if current_user.es_dueno():
        consulta = Solicitud.query.filter_by(
            dueno_id=current_user.id
        )

    elif current_user.es_cuidador():
        perfil = PerfilCuidador.query.filter_by(
            usuario_id=current_user.id
        ).first()

        if perfil is None:
            return jsonify({
                "solicitudes": []
            }), 200

        consulta = Solicitud.query.filter_by(
            cuidador_id=perfil.id
        )

    else:
        return error(
            "Acceso no autorizado.",
            403,
        )

    solicitudes = consulta.order_by(
        Solicitud.id.desc()
    ).all()

    return jsonify({
        "solicitudes": [
            solicitud_a_dict(s)
            for s in solicitudes
        ]
    }), 200


@solicitudes_bp.get("/<int:solicitud_id>")
@login_required
def obtener_solicitud(solicitud_id):
    solicitud = db.session.get(
        Solicitud,
        solicitud_id,
    )

    if (
        solicitud is None
        or not puede_ver(solicitud)
    ):
        return error(
            "Solicitud no encontrada.",
            404,
        )

    return jsonify({
        "solicitud": solicitud_a_dict(solicitud)
    }), 200


def cambiar_estado(solicitud_id, accion):
    """
    Gestiona los estados de alojamiento y visitas.

    El cuidador acepta, rechaza o finaliza.
    Ambos participantes pueden cancelar una reserva aceptada antes del inicio.
    El dueño también puede cancelar una solicitud pendiente.
    """
    solicitud_previa = db.session.get(
        Solicitud,
        solicitud_id,
    )

    if solicitud_previa is None:
        return error(
            "Solicitud no encontrada.",
            404,
        )

    if not puede_ver(solicitud_previa):
        return error(
            "Solicitud no encontrada.",
            404,
        )

    perfil_id = solicitud_previa.cuidador_id

    try:
        # Bloquear el perfil del cuidador.
        perfil = db.session.execute(
            select(PerfilCuidador)
            .where(
                PerfilCuidador.id == perfil_id
            )
            .with_for_update()
        ).scalar_one()

        # Actualizar la solicitud dentro del bloqueo.
        db.session.expire(solicitud_previa)

        solicitud = db.session.execute(
            select(Solicitud)
            .where(
                Solicitud.id == solicitud_id
            )
            .with_for_update()
        ).scalar_one()

        if not puede_ver(solicitud):
            db.session.rollback()
            return error(
                "Solicitud no encontrada.",
                404,
            )

        anterior = solicitud.estado

        es_dueno = (
            current_user.id == solicitud.dueno_id
        )

        es_cuidador = (
            current_user.es_cuidador()
            and perfil.usuario_id == current_user.id
        )

        if accion == "aceptar":
            if (
                not es_cuidador
                or anterior != "PENDIENTE"
            ):
                db.session.rollback()
                return error(
                    "No se puede aceptar esta solicitud.",
                    409,
                )

            ids = [
                item.mascota_id
                for item in solicitud.mascotas_asociadas
            ]

            bloquear_mascotas(ids)

            if solicitud.modalidad == "ALOJAMIENTO":
                if solicitud.fecha_desde < date.today():
                    db.session.rollback()
                    return error(
                        "La estadia esta en el pasado.",
                        409,
                    )

                if not cubre_alojamiento(
                    perfil.id,
                    solicitud.fecha_desde,
                    solicitud.fecha_hasta,
                ):
                    db.session.rollback()
                    return error(
                        "Ya no existe esa disponibilidad.",
                        409,
                    )

                reservas = reservas_que_ocupan(
                    perfil.id,
                    solicitud.fecha_desde,
                    solicitud.fecha_hasta,
                )

                if not hay_cupo(
                    perfil,
                    solicitud.fecha_desde,
                    solicitud.fecha_hasta,
                    solicitud.total_mascotas,
                    reservas,
                ):
                    db.session.rollback()
                    return error(
                        "No hay cupos suficientes.",
                        409,
                    )

                if mascota_ya_reservada(
                    ids,
                    solicitud.fecha_desde,
                    solicitud.fecha_hasta,
                ):
                    db.session.rollback()
                    return error(
                        "Una mascota ya tiene una reserva.",
                        409,
                    )

                from backend.app.visitas.logica import (
                    conflicto_mascotas_alojamiento,
                )

                if conflicto_mascotas_alojamiento(
                    ids,
                    solicitud.fecha_desde,
                    solicitud.fecha_hasta,
                ):
                    db.session.rollback()
                    return error(
                        "Una mascota tiene una visita aceptada.",
                        409,
                    )

            elif solicitud.modalidad == "VISITA":
                from backend.app.visitas.logica import (
                    conflicto_mascotas_visita,
                    horario_cubierto,
                    turnos_superpuestos,
                )

                fecha = solicitud.fecha_desde
                inicio = solicitud.hora_desde
                fin = solicitud.hora_hasta

                if (
                    datetime.combine(fecha, inicio)
                    <= datetime.now()
                ):
                    db.session.rollback()
                    return error(
                        "La visita ya comenzo o paso.",
                        409,
                    )

                if perfil.tarifa_visita is None:
                    db.session.rollback()
                    return error(
                        "El cuidador no ofrece visitas.",
                        409,
                    )

                if not horario_cubierto(
                    perfil.id,
                    fecha,
                    inicio,
                    fin,
                ):
                    db.session.rollback()
                    return error(
                        "El horario ya no esta disponible.",
                        409,
                    )

                if turnos_superpuestos(
                    perfil.id,
                    fecha,
                    inicio,
                    fin,
                ):
                    db.session.rollback()
                    return error(
                        "El cuidador ya tiene una visita.",
                        409,
                    )

                if conflicto_mascotas_visita(
                    ids,
                    fecha,
                    inicio,
                    fin,
                ):
                    db.session.rollback()
                    return error(
                        "Una mascota ya tiene un servicio.",
                        409,
                    )

            else:
                db.session.rollback()
                return error(
                    "Modalidad no reconocida.",
                    400,
                )

            nuevo = "ACEPTADA"

        elif accion == "rechazar":
            if (
                not es_cuidador
                or anterior != "PENDIENTE"
            ):
                db.session.rollback()
                return error(
                    "No se puede rechazar esta solicitud.",
                    409,
                )

            nuevo = "RECHAZADA"

        elif accion == "cancelar":
            puede_cancelar = (
                es_dueno and anterior in ("PENDIENTE", "ACEPTADA")
            ) or (
                es_cuidador and anterior == "ACEPTADA"
            )
            if not puede_cancelar:
                db.session.rollback()
                return error(
                    "No se puede cancelar esta solicitud.",
                    409,
                )

            if anterior == "ACEPTADA":
                if solicitud.modalidad == "VISITA":
                    inicio_servicio = datetime.combine(
                        solicitud.fecha_desde,
                        solicitud.hora_desde,
                    )

                    iniciada = (
                        inicio_servicio <= datetime.now()
                    )
                else:
                    iniciada = (
                        solicitud.fecha_desde <= date.today()
                    )

                if iniciada:
                    db.session.rollback()
                    return error(
                        "El servicio ya iniciado "
                        "no puede cancelarse.",
                        409,
                    )

            nuevo = "CANCELADA"

        elif accion == "finalizar":
            if (
                not es_cuidador
                or anterior != "ACEPTADA"
            ):
                db.session.rollback()
                return error(
                    "No se puede finalizar esta solicitud.",
                    409,
                )

            if solicitud.modalidad == "VISITA":
                fin_servicio = datetime.combine(
                    solicitud.fecha_hasta,
                    solicitud.hora_hasta,
                )

                servicio_pendiente = (
                    fin_servicio > datetime.now()
                )
            else:
                servicio_pendiente = (
                    solicitud.fecha_hasta > date.today()
                )

            if servicio_pendiente:
                db.session.rollback()
                return error(
                    "El servicio todavia no termino.",
                    409,
                )

            nuevo = "FINALIZADA"

        else:
            db.session.rollback()
            return error(
                "Accion no valida.",
                400,
            )

        solicitud.estado = nuevo

        registrar_estado(
            solicitud,
            anterior,
            nuevo,
        )

        db.session.commit()

        return jsonify({
            "mensaje": (
                f"Solicitud {nuevo.lower()} correctamente."
            ),
            "solicitud": solicitud_a_dict(solicitud),
        }), 200

    except (IntegrityError, OperationalError):
        db.session.rollback()
        return error(
            "No se pudo actualizar la solicitud.",
            409,
        )


@solicitudes_bp.post("/<int:solicitud_id>/aceptar")
@login_required
def aceptar(solicitud_id):
    return cambiar_estado(
        solicitud_id,
        "aceptar",
    )


@solicitudes_bp.post("/<int:solicitud_id>/rechazar")
@login_required
def rechazar(solicitud_id):
    return cambiar_estado(
        solicitud_id,
        "rechazar",
    )


@solicitudes_bp.post("/<int:solicitud_id>/cancelar")
@login_required
def cancelar(solicitud_id):
    return cambiar_estado(
        solicitud_id,
        "cancelar",
    )


@solicitudes_bp.post("/<int:solicitud_id>/finalizar")
@login_required
def finalizar(solicitud_id):
    return cambiar_estado(
        solicitud_id,
        "finalizar",
    )
