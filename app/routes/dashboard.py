from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_login import login_required, current_user, logout_user
from app import db
from datetime import datetime
from app.models.products import Productos
from app.models.usuarios import User
import traceback  # ✅ Para mostrar errores en consola

dashboard_bp = Blueprint('dashboard', __name__)

# =======================
# DASHBOARD PRINCIPAL
# =======================
@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.nameUser)


# =======================
# ESTADÍSTICAS DEL DASHBOARD
# =======================
@dashboard_bp.route('/api/dashboard/stats')
@login_required
def dashboard_stats():
    try:
        try:
            from app.models import Order
        except ImportError:
            Order = None

        total_products = Productos.query.count()
        total_orders = Order.query.count() if Order else 0
        total_users = User.query.count()

        today = datetime.now().date()
        if Order:
            today_orders = Order.query.filter(Order.orderDate >= today).all()
            today_income = sum(float(order.totalAmount) for order in today_orders)
        else:
            today_income = 0

        return jsonify({
            'total_products': total_products,
            'total_orders': total_orders,
            'total_users': total_users,
            'today_income': today_income,
            'recent_orders': [],
            'popular_products': []
        })
    except Exception as e:
        print(f"⚠️ Error en dashboard_stats: {e}")
        traceback.print_exc()
        return jsonify({
            'total_products': 0,
            'total_orders': 0,
            'total_users': 0,
            'today_income': 0,
            'recent_orders': [],
            'popular_products': []
        })


# =======================
# CRUD DE PRODUCTOS
# =======================
@dashboard_bp.route('/api/products', methods=['GET'])
@login_required
def get_products():
    try:
        products = Productos.query.all()
        return jsonify([
            {
                'id': p.idProduct,
                'name': p.nameProduct,
                'category': p.category,
                'price': float(p.price),
                'stock': p.stock,
                'status': p.status,
                'description': p.description or '',
                'image': p.image or f'https://via.placeholder.com/250x300/f8f9fa/000?text={p.nameProduct}'
            }
            for p in products
        ])
    except Exception as e:
        print(f"⚠️ Error obteniendo productos: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/products', methods=['POST'])
@login_required
def add_product():
    try:
        data = request.get_json()
        new_product = Productos(
            nameProduct=data['name'],
            category=data['category'],
            price=data['price'],
            stock=data['stock'],
            status=data['status'],
            description=data.get('description', ''),
            image=data.get('image', ''),
            created_at=datetime.now()
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': 'Producto agregado correctamente'})
    except Exception as e:
        print(f"⚠️ Error agregando producto: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/products/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    try:
        product = Productos.query.get_or_404(product_id)
        data = request.get_json()

        product.nameProduct = data['name']
        product.category = data['category']
        product.price = data['price']
        product.stock = data['stock']
        product.status = data['status']
        product.description = data.get('description', '')
        product.image = data.get('image', '')

        db.session.commit()
        return jsonify({'message': 'Producto actualizado correctamente'})
    except Exception as e:
        print(f"⚠️ Error actualizando producto: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/products/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    try:
        product = Productos.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Producto eliminado correctamente'})
    except Exception as e:
        print(f"⚠️ Error eliminando producto: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# =======================
# CRUD DE USUARIOS
# =======================
@dashboard_bp.route('/api/users', methods=['GET'])
@login_required
def get_users():
    try:
        users = User.query.all()
        return jsonify([
            {
                'id': u.idUser,
                'name': u.nameUser,
                'email': u.emailUser,
                'role': 'Administrador' if u.is_admin else 'Usuario',
                'created_at': u.created_at.strftime('%Y-%m-%d %H:%M') if u.created_at else 'N/A',
                'status': 'Activo'
            }
            for u in users
        ])
    except Exception as e:
        print(f"⚠️ Error obteniendo usuarios: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    try:
        print(f"🧹 Intentando eliminar usuario con ID: {user_id}")
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado'
            }), 404

        if user.idUser == current_user.idUser:
            return jsonify({
                'success': False,
                'error': 'No puedes eliminar tu propio usuario'
            }), 400

        # ELIMINAR MANUALMENTE LOS CART ITEMS PRIMERO
        try:
            # Importar CartItem dentro del try para evitar errores de importación
            from app.models.usuarios import CartItem
            # Contar y eliminar items del carrito
            cart_items = CartItem.query.filter_by(idUser=user_id).all()
            for item in cart_items:
                db.session.delete(item)
            print(f"🗑️ Eliminados {len(cart_items)} items del carrito")
        except Exception as cart_error:
            print(f"⚠️ Error con cart items: {cart_error}")
            # Continuar aunque falle

        # Ahora eliminar el usuario
        db.session.delete(user)
        db.session.commit()
        
        print(f"✅ Usuario eliminado correctamente: {user.nameUser}")
        return jsonify({
            'success': True,
            'message': f'Usuario {user.nameUser} eliminado correctamente'
        })

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al eliminar usuario: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error del servidor: {str(e)}'
        }), 500
# =======================
# CATEGORÍAS
# =======================
@dashboard_bp.route('/api/categories', methods=['GET'])
@login_required
def get_categories():
    try:
        from app.models import Category
        categories = Category.query.all()
        return jsonify([
            {
                'id': c.idCategory,
                'name': c.name,
                'description': c.description,
                'products_count': getattr(c, 'products_count', 0),
                'status': c.status
            }
            for c in categories
        ])
    except Exception as e:
        print(f"⚠️ Error obteniendo categorías: {e}")
        traceback.print_exc()
        return jsonify([
            {'id': 'C001', 'name': 'Vestidos', 'description': 'Vestidos para mujer', 'products_count': 56, 'status': 'Activa'},
            {'id': 'C002', 'name': 'Pantalones', 'description': 'Pantalones de moda', 'products_count': 42, 'status': 'Activa'},
            {'id': 'C003', 'name': 'Camisas', 'description': 'Camisas elegantes', 'products_count': 38, 'status': 'Activa'}
        ])


# =======================
# REPORTES Y CONFIGURACIÓN
# =======================
@dashboard_bp.route('/api/reports/sales', methods=['GET'])
@login_required
def get_sales_report():
    try:
        return jsonify({
            'total_sales': 15000.75,
            'average_order': 125.50,
            'top_categories': [
                {'name': 'Vestidos', 'sales': 6500.25},
                {'name': 'Pantalones', 'sales': 4200.50},
                {'name': 'Camisas', 'sales': 4300.00}
            ],
            'sales_trend': [1200, 1900, 3000, 2500, 2800, 3200]
        })
    except Exception as e:
        print(f"⚠️ Error generando reporte: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/config', methods=['GET'])
@login_required
def get_config():
    try:
        return jsonify({
            'store_name': 'Fashion Boutique',
            'currency': 'COP',
            'tax_rate': 0.19,
            'shipping_cost': 50.00,
            'free_shipping_min': 500.00
        })
    except Exception as e:
        print(f"⚠️ Error obteniendo configuración: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# =======================
# CERRAR SESIÓN
# =======================
@dashboard_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
