from datetime import datetime
from backend.app.extensions import db

class Valoracion(db.Model):
    __tablename__ = 'valoraciones'

    id = db.Column(db.Integer, primary_key=True)
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitudes.id'), unique=True, nullable=False)
    dueno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    cuidador_id = db.Column(db.Integer, db.ForeignKey('perfiles_cuidadores.id'), nullable=False)
    puntaje = db.Column(db.SmallInteger, nullable=False)  # 1 a 5
    comentario = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.CheckConstraint('puntaje >= 1 AND puntaje <= 5', name='chk_puntaje_rango'),
    )

    def __repr__(self):
        return f'<Valoracion solicitud={self.solicitud_id} puntaje={self.puntaje}>'