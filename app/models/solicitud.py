from datetime import datetime
from app.extensions import db

class Solicitud(db.Model):
    __tablename__ = 'solicitudes'

    id = db.Column(db.Integer, primary_key=True)
    dueno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    cuidador_id = db.Column(db.Integer, db.ForeignKey('perfiles_cuidadores.id'), nullable=False, index=True)
    modalidad = db.Column(db.String(20), default='ALOJAMIENTO', nullable=False)
    fecha_desde = db.Column(db.Date, nullable=False, index=True)
    fecha_hasta = db.Column(db.Date, nullable=False, index=True)
    estado = db.Column(db.String(20), default='PENDIENTE', nullable=False, index=True)
    # Estados válidos: 'PENDIENTE', 'ACEPTADA', 'RECHAZADA', 'CANCELADA', 'EN_CURSO', 'FINALIZADA'
    
    total_mascotas = db.Column(db.Integer, default=1, nullable=False)
    monto_total = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Protocolo de imprevistos y salud
    contacto_emergencia = db.Column(db.String(100), nullable=False)
    veterinario_emergencia = db.Column(db.String(100), nullable=True)
    autorizacion_urgencia = db.Column(db.Boolean, default=True, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    mascotas_asociadas = db.relationship('SolicitudMascota', backref='solicitud', lazy=True, cascade='all, delete-orphan')
    valoracion = db.relationship('Valoracion', backref='solicitud', uselist=False, lazy=True)
    incidencias = db.relationship('Incidencia', backref='solicitud', lazy=True)

    def __repr__(self):
        return f'<Solicitud id={self.id} estado={self.estado} ({self.fecha_desde} a {self.fecha_hasta})>'

class SolicitudMascota(db.Model):
    __tablename__ = 'solicitudes_mascotas'

    id = db.Column(db.Integer, primary_key=True)
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitudes.id'), nullable=False)
    mascota_id = db.Column(db.Integer, db.ForeignKey('mascotas.id'), nullable=False)
    
    # Snapshot inmutable de la mascota en el momento del servicio
    nombre_snapshot = db.Column(db.String(50), nullable=False)
    especie_snapshot = db.Column(db.String(20), nullable=False)
    cuidados_snapshot = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<SolicitudMascota solicitud={self.solicitud_id} mascota={self.nombre_snapshot}>'