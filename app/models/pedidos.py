from app import db
from datetime import datetime

class Pedido(db.Model):
    __tablename__ = 'pedido'
    
    idPedido = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)  # Usuario que realizó el pedido
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(
        db.Enum('Pendiente', 'Pagado', 'Enviado', 'Entregado', 'Cancelado'),
        default='Pendiente'
    )
    
    # Relación con los detalles del pedido
    detalles = db.relationship('DetallePedido', backref='pedido_ref', lazy=True)
    
    def __repr__(self):
        return f'<Pedido {self.idPedido} - Usuario {self.idUser}>'


class DetallePedido(db.Model):
    __tablename__ = 'detalle_pedido'
    
    idDetalle = db.Column(db.Integer, primary_key=True)
    idPedido = db.Column(db.Integer, db.ForeignKey('pedido.idPedido'), nullable=False)
    idProduct = db.Column(db.Integer, db.ForeignKey('product.idProduct'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    
    def __repr__(self):
        return f'<DetallePedido Pedido:{self.idPedido} Producto:{self.idProduct}>'
