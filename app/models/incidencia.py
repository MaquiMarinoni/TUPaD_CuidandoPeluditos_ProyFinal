from datetime import datetime
from app.extensions import db

class Incidencia(db.Model):
    __tablename__ = 'incidencias'

    id = db.Column(db.Integer, primary_key=True)
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitudes.id'), nullable=False)
    reportado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)  # 'SALUD', 'CONDUCTA', 'EXTRAVIO', 'OTRO'
    descripcion = db.Column(db.Text, nullable=False)
    medidas_tomadas = db.Column(db.Text, nullable=True)
    estado = db.Column(db.String(20), default='ABIERTA', nullable=False)  # 'ABIERTA', 'RESUELTA'
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Incidencia id={self.id} tipo={self.tipo}>'