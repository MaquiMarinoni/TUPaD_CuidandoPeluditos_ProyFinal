
"""Panel de administracion. Todas las consultas requieren rol ADMIN."""

from functools import wraps

from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import func, or_, select

from backend.app.extensions import db
from backend.app.models import (
    Usuario, PerfilCuidador, Solicitud, Incidencia, Mascota, Valoracion
)

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
    template_folder="templates",
    static_folder="static",
    static_url_path="/assets"
)


def solo_admin(funcion):
    @wraps(funcion)
    @login_required
    def protegida(*args, **kwargs):
        if not current_user.activo or current_user.rol.nombre != "ADMIN":
            return jsonify({
                "error": "Acceso exclusivo para administradores."
            }), 403
        return funcion(*args, **kwargs)
    return protegida


def total(modelo):
    return db.session.scalar(
        select(func.count()).select_from(modelo)
    ) or 0


def pagina():
    return min(max(request.args.get("pagina", 1, type=int), 1), 100000)


def respuesta_paginada(consulta, convertir):
    pag = db.paginate(
        consulta,
        page=pagina(),
        per_page=20,
        error_out=False
    )
    return jsonify({
        "items": [convertir(item) for item in pag.items],
        "pagina": pag.page,
        "paginas": pag.pages,
        "total": pag.total
    })


def serializar_historial(solicitud):
    """Devuelve los cambios de estado registrados para una solicitud."""
    return [
        {
            "estado_anterior": cambio.estado_anterior,
            "estado_nuevo": cambio.estado_nuevo,
            "motivo": cambio.motivo,
            "fecha_cambio": cambio.fecha_cambio.isoformat(),
            "usuario_id": cambio.usuario_id
        }
        for cambio in solicitud.historial_estados
    ]


# ---------------------------------------------------------
# Panel principal e indicadores
# ---------------------------------------------------------

@admin_bp.get("")
@admin_bp.get("/")
@solo_admin
def panel():
    return render_template("admin.html")


@admin_bp.get("/api/resumen")
@solo_admin
def resumen():
    return jsonify({
        "usuarios": total(Usuario),
        "usuarios_activos": db.session.scalar(
            select(func.count())
            .select_from(Usuario)
            .where(Usuario.activo.is_(True))
        ) or 0,
        "cuidadores": total(PerfilCuidador),
        "mascotas": total(Mascota),
        "solicitudes": total(Solicitud),
        "solicitudes_pendientes": db.session.scalar(
            select(func.count())
            .select_from(Solicitud)
            .where(Solicitud.estado == "PENDIENTE")
        ) or 0,
        "incidencias": total(Incidencia),
        "incidencias_abiertas": db.session.scalar(
            select(func.count())
            .select_from(Incidencia)
            .where(Incidencia.estado == "ABIERTA")
        ) or 0,
        "valoraciones": total(Valoracion)
    })


# ---------------------------------------------------------
# Usuarios y administracion de cuentas
# ---------------------------------------------------------

@admin_bp.get("/api/usuarios")
@solo_admin
def usuarios():
    consulta = select(Usuario).order_by(Usuario.id.desc())

    rol = request.args.get("rol", "").strip().upper()

    if rol:
        if rol not in {"ADMIN", "DUENO", "CUIDADOR"}:
            return jsonify({"error": "Rol no valido."}), 400

        consulta = consulta.where(Usuario.rol.has(nombre=rol))

    buscar = request.args.get("buscar", "").strip()[:100]

    if buscar:
        patron = f"%{buscar}%"
        consulta = consulta.where(or_(
            Usuario.nombre.ilike(patron),
            Usuario.apellido.ilike(patron),
            Usuario.email.ilike(patron)
        ))

    return respuesta_paginada(consulta, lambda u: {
        "id": u.id,
        "nombre": u.nombre,
        "apellido": u.apellido,
        "email": u.email,
        "rol": u.rol.nombre,
        "provincia": u.provincia,
        "localidad": u.localidad,
        "activo": u.activo
    })


@admin_bp.patch("/api/usuarios/<int:usuario_id>/estado")
@solo_admin
def estado_usuario(usuario_id):
    datos = request.get_json(silent=True)

    if (
        not isinstance(datos, dict)
        or set(datos) != {"activo"}
        or type(datos["activo"]) is not bool
    ):
        return jsonify({
            "error": "Se requiere el campo booleano activo."
        }), 400

    usuario = db.session.get(Usuario, usuario_id)

    if usuario is None:
        return jsonify({"error": "Usuario no encontrado."}), 404

    if usuario.id == current_user.id or usuario.rol.nombre == "ADMIN":
        return jsonify({
            "error": "No se permite modificar cuentas administradoras."
        }), 403

    usuario.activo = datos["activo"]
    db.session.commit()

    return jsonify({
        "mensaje": "Estado actualizado.",
        "id": usuario.id,
        "activo": usuario.activo
    })


# ---------------------------------------------------------
# Listado general de cuidadores
# ---------------------------------------------------------

@admin_bp.get("/api/cuidadores")
@solo_admin
def cuidadores():
    consulta = (
        select(PerfilCuidador)
        .join(Usuario)
        .order_by(PerfilCuidador.id.desc())
    )

    return respuesta_paginada(consulta, lambda p: {
        "id": p.id,
        "usuario_id": p.usuario_id,
        "nombre": f"{p.usuario.nombre} {p.usuario.apellido}",
        "email": p.usuario.email,
        "activo": p.usuario.activo,
        "provincia": p.usuario.provincia,
        "localidad": p.usuario.localidad,
        "capacidad": p.capacidad_maxima,
        "tarifa_diaria": str(p.tarifa_diaria),
        "tarifa_visita": (
            str(p.tarifa_visita)
            if p.tarifa_visita is not None else None
        )
    })


# ---------------------------------------------------------
# Listados generales de solicitudes e incidencias
# ---------------------------------------------------------

@admin_bp.get("/api/solicitudes")
@solo_admin
def solicitudes():
    consulta = select(Solicitud).order_by(Solicitud.id.desc())

    estado = request.args.get("estado", "").strip().upper()

    if estado:
        if estado not in {
            "PENDIENTE",
            "ACEPTADA",
            "RECHAZADA",
            "CANCELADA",
            "FINALIZADA"
        }:
            return jsonify({"error": "Estado no valido."}), 400

        consulta = consulta.where(Solicitud.estado == estado)

    return respuesta_paginada(consulta, lambda s: {
        "id": s.id,
        "dueno_id": s.dueno_id,
        "cuidador_id": s.cuidador_id,
        "modalidad": s.modalidad,
        "estado": s.estado,
        "fecha_desde": s.fecha_desde.isoformat(),
        "fecha_hasta": s.fecha_hasta.isoformat(),
        "total_mascotas": s.total_mascotas
    })


@admin_bp.get("/api/incidencias")
@solo_admin
def incidencias():
    consulta = select(Incidencia).order_by(Incidencia.id.desc())

    estado = request.args.get("estado", "").strip().upper()

    if estado:
        if estado not in {"ABIERTA", "RESUELTA"}:
            return jsonify({"error": "Estado no valido."}), 400

        consulta = consulta.where(Incidencia.estado == estado)

    return respuesta_paginada(consulta, lambda i: {
        "id": i.id,
        "solicitud_id": i.solicitud_id,
        "tipo": i.tipo,
        "estado": i.estado,
        "fecha": i.fecha_registro.isoformat(),
        "descripcion": i.descripcion
    })


# ---------------------------------------------------------
# Detalle de dueños y mascotas
# ---------------------------------------------------------

@admin_bp.get("/api/duenos/<int:usuario_id>")
@solo_admin
def detalle_dueno(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)

    if usuario is None or usuario.rol.nombre != "DUENO":
        return jsonify({"error": "Dueño no encontrado."}), 404

    mascotas = db.session.scalars(
        select(Mascota)
        .where(Mascota.dueno_id == usuario.id)
        .order_by(Mascota.id.desc())
    ).all()

    return jsonify({
        "id": usuario.id,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "email": usuario.email,
        "telefono": usuario.telefono,
        "provincia": usuario.provincia,
        "localidad": usuario.localidad,
        "activo": usuario.activo,
        "fecha_registro": usuario.created_at.isoformat(),
        "mascotas": [
            {
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
                "activo": mascota.activo
            }
            for mascota in mascotas
        ]
    })


# ---------------------------------------------------------
# Historial de solicitudes de un dueño
# ---------------------------------------------------------

@admin_bp.get("/api/duenos/<int:usuario_id>/solicitudes")
@solo_admin
def solicitudes_dueno(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)

    if usuario is None or usuario.rol.nombre != "DUENO":
        return jsonify({"error": "Dueño no encontrado."}), 404

    consulta = (
        select(Solicitud)
        .where(Solicitud.dueno_id == usuario.id)
        .order_by(Solicitud.id.desc())
    )

    return respuesta_paginada(consulta, lambda s: {
        "id": s.id,
        "modalidad": s.modalidad,
        "estado": s.estado,
        "fecha_desde": s.fecha_desde.isoformat(),
        "fecha_hasta": s.fecha_hasta.isoformat(),
        "hora_desde": (
            s.hora_desde.isoformat() if s.hora_desde else None
        ),
        "hora_hasta": (
            s.hora_hasta.isoformat() if s.hora_hasta else None
        ),
        "total_mascotas": s.total_mascotas,
        "monto_total": (
            str(s.monto_total) if s.monto_total is not None else None
        ),
        "cuidador": {
            "id": s.cuidador_perfil.id,
            "nombre": (
                f"{s.cuidador_perfil.usuario.nombre} "
                f"{s.cuidador_perfil.usuario.apellido}"
            )
        },
        "mascotas": [
            {
                "nombre": asociacion.nombre_snapshot,
                "especie": asociacion.especie_snapshot
            }
            for asociacion in s.mascotas_asociadas
        ],
        "historial_estados": serializar_historial(s)
    })


# ---------------------------------------------------------
# Detalle de cuidadores
# ---------------------------------------------------------

@admin_bp.get("/api/cuidadores/<int:perfil_id>")
@solo_admin
def detalle_cuidador(perfil_id):
    perfil = db.session.get(PerfilCuidador, perfil_id)

    if perfil is None or perfil.usuario.rol.nombre != "CUIDADOR":
        return jsonify({"error": "Cuidador no encontrado."}), 404

    usuario = perfil.usuario

    return jsonify({
        "id": perfil.id,
        "usuario_id": usuario.id,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "email": usuario.email,
        "telefono": usuario.telefono,
        "provincia": usuario.provincia,
        "localidad": usuario.localidad,
        "activo": usuario.activo,
        "fecha_registro": usuario.created_at.isoformat(),
        "descripcion": perfil.descripcion,
        "capacidad_maxima": perfil.capacidad_maxima,
        "admite_perros": perfil.admite_perros,
        "admite_gatos": perfil.admite_gatos,
        "condiciones_convivencia": perfil.condiciones_convivencia,
        "tarifa_diaria": str(perfil.tarifa_diaria),
        "tarifa_visita": (
            str(perfil.tarifa_visita)
            if perfil.tarifa_visita is not None else None
        )
    })


# ---------------------------------------------------------
# Historial de servicios e incidencias del cuidador
# ---------------------------------------------------------

@admin_bp.get("/api/cuidadores/<int:perfil_id>/servicios")
@solo_admin
def servicios_cuidador(perfil_id):
    perfil = db.session.get(PerfilCuidador, perfil_id)

    if perfil is None or perfil.usuario.rol.nombre != "CUIDADOR":
        return jsonify({"error": "Cuidador no encontrado."}), 404

    consulta = (
        select(Solicitud)
        .where(Solicitud.cuidador_id == perfil.id)
        .order_by(Solicitud.id.desc())
    )

    return respuesta_paginada(consulta, lambda s: {
        "id": s.id,
        "modalidad": s.modalidad,
        "estado": s.estado,
        "fecha_desde": s.fecha_desde.isoformat(),
        "fecha_hasta": s.fecha_hasta.isoformat(),
        "hora_desde": (
            s.hora_desde.isoformat() if s.hora_desde else None
        ),
        "hora_hasta": (
            s.hora_hasta.isoformat() if s.hora_hasta else None
        ),
        "total_mascotas": s.total_mascotas,
        "monto_total": (
            str(s.monto_total) if s.monto_total is not None else None
        ),
        "dueno": {
            "id": s.dueno.id,
            "nombre": f"{s.dueno.nombre} {s.dueno.apellido}"
        },
        "incidencias": [
            {
                "id": incidencia.id,
                "tipo": incidencia.tipo,
                "descripcion": incidencia.descripcion,
                "medidas_tomadas": incidencia.medidas_tomadas,
                "comentario_cierre": incidencia.comentario_cierre,
                "estado": incidencia.estado,
                "fecha": incidencia.fecha_registro.isoformat(),
                "reportado_por_id": incidencia.reportado_por_id
            }
            for incidencia in s.incidencias
        ],
        "historial_estados": serializar_historial(s)
    })
