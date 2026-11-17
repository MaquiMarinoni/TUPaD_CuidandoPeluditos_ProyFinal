"""Cambios administrativos de estado, conservados como historial."""
from datetime import datetime, timezone
from backend.app.extensions import db


def ahora_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class AuditoriaCuenta(db.Model):
    __tablename__ = 'auditoria_cuentas'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    administrador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    activo_anterior = db.Column(db.Boolean, nullable=False)
    activo_nuevo = db.Column(db.Boolean, nullable=False)
    motivo = db.Column(db.String(1000), nullable=False)
    fecha_cambio = db.Column(db.DateTime, nullable=False, default=ahora_utc)
    administrador = db.relationship('Usuario', foreign_keys=[administrador_id])
