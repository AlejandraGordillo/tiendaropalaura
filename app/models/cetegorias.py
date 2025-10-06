from app import db
from datetime import datetime

class Categoria(db.Model):
    __tablename__ = 'categorias'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f'<Categoria {self.nombre}>'

class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    imagen = db.Column(db.String(255), nullable=True)
    estado = db.Column(db.Enum('Activo', 'Inactivo'), nullable=False, default='Activo')

    categoria = db.relationship('Categoria', backref=db.backref('productos', lazy=True))

    def __repr__(self):
        return f'<Producto {self.nombre}>'


