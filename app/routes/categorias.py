from flask import Blueprint, jsonify, request
from flask_login import login_required
from app import db
from app.models.categoria import Categoria

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/api/categories', methods=['GET'])
def get_categories():
    """Obtener todas las categorías"""
    try:
        categories = Categoria.query.order_by(Categoria.name).all()
        return jsonify([{
            'id': category.id,
            'name': category.name
        } for category in categories])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@categories_bp.route('/api/categories', methods=['POST'])
@login_required
def add_category():
    """Agregar nueva categoría"""
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        name = data.get('name', '').strip()
        if not name:
            return jsonify({'success': False, 'message': 'El nombre de la categoría es obligatorio'}), 400

        # Verificar si ya existe la categoría
        existing = Categoria.query.filter_by(name=name).first()
        if existing:
            return jsonify({'success': False, 'message': 'La categoría ya existe'}), 400

        new_category = Categoria(name=name)
        db.session.add(new_category)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Categoría agregada correctamente',
            'category': {
                'id': new_category.id,
                'name': new_category.name
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al agregar la categoría: {str(e)}'}), 500

@categories_bp.route('/api/categories/<int:category_id>', methods=['PUT'])
@login_required
def update_category(category_id):
    """Actualizar categoría existente"""
    try:
        category = Categoria.query.get_or_404(category_id)

        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        name = data.get('name', '').strip()
        if not name:
            return jsonify({'success': False, 'message': 'El nombre de la categoría es obligatorio'}), 400

        # Verificar si el nuevo nombre ya existe en otra categoría
        existing = Categoria.query.filter(Categoria.name == name, Categoria.id != category_id).first()
        if existing:
            return jsonify({'success': False, 'message': 'Otra categoría con ese nombre ya existe'}), 400

        category.name = name
        db.session.commit()

        return jsonify({'success': True, 'message': 'Categoría actualizada correctamente'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al actualizar la categoría: {str(e)}'}), 500

@categories_bp.route('/api/categories/<int:category_id>', methods=['DELETE'])
@login_required
def delete_category(category_id):
    """Eliminar categoría"""
    try:
        category = Categoria.query.get_or_404(category_id)

        # Opcional: verificar si tiene productos asociados antes de eliminar
        if category.products and len(category.products) > 0:
            return jsonify({'success': False, 'message': 'No se puede eliminar una categoría con productos asociados'}), 400

        db.session.delete(category)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Categoría eliminada correctamente'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al eliminar la categoría: {str(e)}'}), 500
