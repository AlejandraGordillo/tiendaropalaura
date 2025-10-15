from app import db
from datetime import datetime
from decimal import Decimal  # Recomendado para precisión en campos monetarios


class Reporte(db.Model):
    __tablename__ = 'reporte'

    idReporte = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)  # Usuario que genera el reporte
    fecha_generacion = db.Column(db.DateTime, default=datetime.utcnow)  # Fecha automática de creación
    tipo = db.Column(db.String(100), nullable=False)  # Ejemplo: 'Pedidos del día', 'Ventas mensuales', etc.
    total_pedidos = db.Column(db.Integer, nullable=False, default=0)
    total_ventas = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    observaciones = db.Column(db.Text, nullable=True)

    # Relación con detalles del reporte
    detalles = db.relationship('DetalleReporte', backref='reporte', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Reporte {self.idReporte} - Usuario {self.idUser} - {self.tipo}>'


class DetalleReporte(db.Model):
    __tablename__ = 'detalle_reporte'

    idDetalleReporte = db.Column(db.Integer, primary_key=True)
    idReporte = db.Column(db.Integer, db.ForeignKey('reporte.idReporte', ondelete='CASCADE'), nullable=False)
    idPedido = db.Column(db.Integer, db.ForeignKey('pedido.idPedido'), nullable=True)
    descripcion = db.Column(db.String(255), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    
    