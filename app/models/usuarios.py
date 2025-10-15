
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    
    idUser = db.Column(db.Integer, primary_key=True)
    nameUser = db.Column(db.String(50), unique=True, nullable=False)
    emailUser = db.Column(db.String(120), unique=True, nullable=False)
    passwordUser = db.Column(db.String(255), nullable=False)
    
    is_admin = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expiration = db.Column(db.DateTime, nullable=True)
    verification_code = db.Column(db.String(6), nullable=True)
    verification_code_expiration = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con el carrito
    #cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade="all, delete-orphan")
    
    def get_id(self):
        return str(self.idUser)

    def set_password(self, password):
        self.passwordUser = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.passwordUser, password)
    
    def is_administrator(self):
        return self.is_admin
    
    def get_role_display(self):
        return "Administrador" if self.is_admin else "Usuario"
    
    # Métodos para el carrito
    def get_cart(self):
        return CartItem.query.filter_by(idUser=self.idUser).all()
    
    def get_cart_count(self):
        return CartItem.query.filter_by(idUser=self.idUser).count()

    def __repr__(self):
        return f'<User {self.nameUser}>'  

# Modelo para items del carrito
class CartItem(db.Model):
    __tablename__ = 'cart_item'
    __table_args__ = {'extend_existing': True}
    idCartItem = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)
    idProduct = db.Column(db.Integer, db.ForeignKey('product.idProduct'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con producto
    #product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))
