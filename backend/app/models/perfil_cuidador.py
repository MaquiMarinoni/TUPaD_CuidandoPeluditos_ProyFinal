from backend.app.extensions import db

class PerfilCuidador(db.Model):
    __tablename__ = 'perfiles_cuidadores'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    capacidad_maxima = db.Column(db.Integer, default=1, nullable=False)  # Cupo simultáneo
    admite_perros = db.Column(db.Boolean, default=True, nullable=False)
    admite_gatos = db.Column(db.Boolean, default=True, nullable=False)
    condiciones_convivencia = db.Column(db.Text, nullable=True)
    tarifa_diaria = db.Column(db.Numeric(10, 2), nullable=False)

    # Relaciones
    disponibilidades = db.relationship('Disponibilidad', backref='cuidador', lazy=True, cascade='all, delete-orphan')
    solicitudes_recibidas = db.relationship('Solicitud', foreign_keys='Solicitud.cuidador_id', backref='cuidador_perfil', lazy=True)

    def __repr__(self):
        return f'<PerfilCuidador id={self.id} usuario_id={self.usuario_id}>'

class Disponibilidad(db.Model):
    __tablename__ = 'disponibilidades'

    id = db.Column(db.Integer, primary_key=True)
    cuidador_id = db.Column(db.Integer, db.ForeignKey('perfiles_cuidadores.id'), nullable=False, index=True)
    fecha_desde = db.Column(db.Date, nullable=False, index=True)
    fecha_hasta = db.Column(db.Date, nullable=False, index=True)
    modalidad = db.Column(db.String(20), default='ALOJAMIENTO', nullable=False)  # 'ALOJAMIENTO' o 'VISITA'
    activo = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f'<Disponibilidad {self.fecha_desde} a {self.fecha_hasta} ({self.modalidad})>'