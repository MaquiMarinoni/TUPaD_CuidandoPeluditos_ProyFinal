
from datetime import datetime

from backend.app.extensions import db


class Solicitud(db.Model):
    __tablename__ = "solicitudes"

    id = db.Column(db.Integer, primary_key=True)

    dueno_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False,
        index=True
    )

    cuidador_id = db.Column(
        db.Integer,
        db.ForeignKey("perfiles_cuidadores.id"),
        nullable=False,
        index=True
    )

    modalidad = db.Column(
        db.String(20),
        default="ALOJAMIENTO",
        nullable=False
    )

    fecha_desde = db.Column(db.Date, nullable=False, index=True)
    fecha_hasta = db.Column(db.Date, nullable=False, index=True)

    # Horarios para visitas a domicilio.
    hora_desde = db.Column(db.Time, nullable=True)
    hora_hasta = db.Column(db.Time, nullable=True)

    estado = db.Column(
        db.String(20),
        default="PENDIENTE",
        nullable=False,
        index=True
    )

    # Se calcula en backend, no se acepta
    # libremente desde el frontend.
    total_mascotas = db.Column(
        db.Integer,
        default=1,
        nullable=False
    )

    monto_total = db.Column(
        db.Numeric(10, 2),
        nullable=True
    )

    # Datos y autorizaciones de emergencia.
    contacto_emergencia = db.Column(
        db.String(100),
        nullable=False
    )

    veterinario_emergencia = db.Column(
        db.String(100),
        nullable=True
    )

    autorizacion_urgencia = db.Column(
        db.Boolean,
        default=False,
        server_default=db.text("0"),
        nullable=False
    )

    limite_gastos_urgencia = db.Column(
        db.Numeric(10, 2),
        nullable=True
    )

    # Ubicacion historica del servicio.
    direccion_servicio = db.Column(
        db.String(120),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    mascotas_asociadas = db.relationship(
        "SolicitudMascota",
        backref="solicitud",
        lazy=True,
        cascade="all, delete-orphan"
    )

    valoracion = db.relationship(
        "Valoracion",
        backref="solicitud",
        uselist=False,
        lazy=True
    )

    incidencias = db.relationship(
        "Incidencia",
        backref="solicitud",
        lazy=True
    )

    historial_estados = db.relationship(
        "HistorialEstado",
        backref="solicitud",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="HistorialEstado.fecha_cambio"
    )

    def __repr__(self):
        return (
            f"<Solicitud id={self.id} "
            f"estado={self.estado}>"
        )


class SolicitudMascota(db.Model):
    __tablename__ = "solicitudes_mascotas"

    id = db.Column(db.Integer, primary_key=True)

    solicitud_id = db.Column(
        db.Integer,
        db.ForeignKey("solicitudes.id"),
        nullable=False
    )

    mascota_id = db.Column(
        db.Integer,
        db.ForeignKey("mascotas.id"),
        nullable=False
    )

    # Datos historicos congelados al crear la solicitud.
    nombre_snapshot = db.Column(db.String(50), nullable=False)
    especie_snapshot = db.Column(db.String(20), nullable=False)

    cuidados_snapshot = db.Column(db.Text, nullable=True)

    veterinario_snapshot = db.Column(
        db.String(100),
        nullable=True
    )

    # Una mascota no puede repetirse en la misma solicitud.
    __table_args__ = (
        db.UniqueConstraint(
            "solicitud_id",
            "mascota_id",
            name="uq_solicitud_mascota"
        ),
    )

    def __repr__(self):
        return (
            f"<SolicitudMascota solicitud={self.solicitud_id} "
            f"mascota={self.mascota_id}>"
        )
