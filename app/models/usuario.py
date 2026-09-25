from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class Rol(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(30), unique=True, nullable=False)  # 'DUENO', 'CUIDADOR', 'ADMIN'

    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

    def __repr__(self):
        return f'<Rol {self.nombre}>'

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(60), nullable=False)
    apellido = db.Column(db.String(60), nullable=False)
    telefono = db.Column(db.String(30), nullable=False)
    provincia = db.Column(db.String(60), nullable=False, index=True)
    localidad = db.Column(db.String(60), nullable=False, index=True)
    direccion = db.Column(db.String(120), nullable=False)  # Dato privado
    activo = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    perfil_cuidador = db.relationship('PerfilCuidador', backref='usuario', uselist=False, lazy=True)
    mascotas = db.relationship('Mascota', backref='dueno', lazy=True)
    solicitudes_creadas = db.relationship('Solicitud', foreign_keys='Solicitud.dueno_id', backref='dueno', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def es_cuidador(self):
        return self.rol and self.rol.nombre == 'CUIDADOR'

    def es_dueno(self):
        return self.rol and self.rol.nombre == 'DUENO'

    def __repr__(self):
        return f'<Usuario {self.email}>'