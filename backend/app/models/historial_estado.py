
from datetime import datetime

from backend.app.extensions import db


class HistorialEstado(db.Model):
    __tablename__ = "historial_estados"

    id = db.Column(db.Integer, primary_key=True)

    solicitud_id = db.Column(
        db.Integer,
        db.ForeignKey("solicitudes.id"),
        nullable=False,
        index=True
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    estado_anterior = db.Column(
        db.String(20),
        nullable=True
    )

    estado_nuevo = db.Column(
        db.String(20),
        nullable=False
    )

    motivo = db.Column(db.Text, nullable=True)

    fecha_cambio = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    usuario = db.relationship(
        "Usuario",
        backref="cambios_estado"
    )

    def __repr__(self):
        return (
            f"<HistorialEstado solicitud={self.solicitud_id} "
            f"estado={self.estado_nuevo}>"
        )
