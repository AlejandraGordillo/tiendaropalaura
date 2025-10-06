from flask import Blueprint, jsonify, request, session, render_template
from flask_login import current_user, login_required
from app.models.pedidos import Pedido, DetallePedido
from datetime import datetime  # Para timestamps si necesitas

pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('/api/pedidos', methods=['GET'])
@login_required
def get_pedidos():
    pedido = Pedido.query.all()
    detalle = DetallePedido.query.all()
    return "nada"

@pedidos_bp.route('/pedidos/<int:pedido_id>')
@login_required
def pedido_detail_html(pedido_id):
    return "nada"

@pedidos_bp.route('/api/pedidos/<int:pedido_id>', methods=['GET'])
@login_required
def get_pedido_detail(pedido_id):
    return "nada"
