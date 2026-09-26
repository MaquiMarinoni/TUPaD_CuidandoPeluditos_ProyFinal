from backend.app.extensions import db

class Mascota(db.Model):
    __tablename__ = 'mascotas'

    id = db.Column(db.Integer, primary_key=True)
    dueno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    nombre = db.Column(db.String(50), nullable=False)
    especie = db.Column(db.String(20), nullable=False)  # 'PERRO' o 'GATO'
    raza = db.Column(db.String(50), nullable=True)
    tamano = db.Column(db.String(20), default='MEDIANO', nullable=False)  # 'CHICO', 'MEDIANO', 'GRANDE'
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    cuidados_especiales = db.Column(db.Text, nullable=True)
    contacto_veterinario = db.Column(db.String(100), nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f'<Mascota {self.nombre} ({self.especie})>'