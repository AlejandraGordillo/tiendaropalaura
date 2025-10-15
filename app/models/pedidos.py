from app import db
from datetime import datetime

# ==========================
# MODELO PEDIDO
# ==========================
class Pedido(db.Model):
    __tablename__ = 'pedido'
    __table_args__ = {'extend_existing': True}

    idPedido = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, db.ForeignKey('user.idUser', ondelete='CASCADE'), nullable=False)  # Usuario que realizó el pedido
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(
        db.Enum('Pendiente', 'Pagado', 'Enviado', 'Entregado', 'Cancelado', name='estado_pedido'),
        default='Pendiente'
    )

    # ✅ Relación con los detalles del pedido (cascada)
    detalles = db.relationship('DetallePedido', backref='pedido', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Pedido {self.idPedido} - Usuario {self.idUser} - Estado {self.estado}>'

    def calcular_total(self):
        """Calcula el total sumando los precios de los detalles."""
        return sum([detalle.cantidad * float(detalle.precio_unitario) for detalle in self.detalles])


# ==========================
# MODELO DETALLE PEDIDO
# ==========================
class DetallePedido(db.Model):
    __tablename__ = 'detalle_pedido'
    __table_args__ = {'extend_existing': True}

    idDetalle = db.Column(db.Integer, primary_key=True)
    idPedido = db.Column(db.Integer, db.ForeignKey('pedido.idPedido', ondelete='CASCADE'), nullable=False)
    idProduct = db.Column(db.Integer, db.ForeignKey('product.idProduct', ondelete='SET NULL'))
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    # ✅ Relación con el producto (opcional)
    producto = db.relationship('Productos', backref='detalles_pedido', lazy=True)

    def subtotal(self):
        """Devuelve el subtotal de este detalle."""
        return float(self.precio_unitario) * self.cantidad

    def __repr__(self):
        return f'<DetallePedido Pedido:{self.idPedido} Producto:{self.idProduct} Cantidad:{self.cantidad}>'
