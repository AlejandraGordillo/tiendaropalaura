from app import db
from datetime import datetime

class Productos(db.Model):
    __tablename__ = 'product'
    idProduct = db.Column(db.Integer, primary_key=True)
    nameProduct = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10,2))
    stock = db.Column(db.Integer)
    category = db.Column(db.String(50))
    image = db.Column(db.String(255))
    status = db.Column(db.String(20))
    category = db.Column(db.String(50))
    #size = db.Column(db.String(20))
    #color = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    #category_id = db.Column(db.Integer, db.ForeignKey('category.idCategory'))

    def __repr__(self):
        return f'<Product {self.nameProduct}>'
