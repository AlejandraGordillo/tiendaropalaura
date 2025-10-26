from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.models.usuarios import User
from app.models.products import Productos
from app.decorators import admin_required


# 🔹 Blueprint único (ya no se repite)
bp = Blueprint('users', __name__)


# 🔸 Función auxiliar para detectar si el usuario es admin
def is_user_admin(user):
    """Detecta si el usuario es administrador (soporta distintas implementaciones)."""
    try:
        if getattr(user, 'is_admin', False):
            return True
        if hasattr(user, 'is_administrator') and callable(getattr(user, 'is_administrator')):
            return user.is_administrator()
    except Exception:
        pass
    return False


# 🔸 Dashboard general
@bp.route('/dashboard')
@login_required
def dashboard():
    admin_flag = is_user_admin(current_user)
    return render_template(
        'dashboard.html',
        user=current_user,
        username=getattr(current_user, 'nameUser', getattr(current_user, 'username', 'Usuario')),
        is_admin=admin_flag
    )


# 🔸 Dashboard solo para administradores
@bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    try:
        total_admins = User.query.filter_by(is_admin=True).count()
        total_regular = User.query.filter_by(is_admin=False).count()
    except Exception:
        total_admins = 0
        total_regular = total_users

    return render_template(
        'dashboard.html',
        total_users=total_users,
        total_admins=total_admins,
        total_regular=total_regular,
        username=getattr(current_user, 'nameUser', getattr(current_user, 'username', 'Admin'))
    )


# 🔸 Vista: Gestión de usuarios (solo admin)
@bp.route('/admin/usuarios')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template(
        'admin_users.html',
        users=users,
        username=getattr(current_user, 'nameUser', getattr(current_user, 'username', 'Admin'))
    )


# 🔸 Perfil del usuario
@bp.route('/profile')
@login_required
def profile():
    try:
        products_q = Productos.query.filter_by(status='Activo').limit(6).all()
    except Exception:
        products_q = Productos.query.limit(6).all()

    products = []
    for p in products_q:
        products.append({
            'id': p.idProduct,
            'name': p.nameProduct,
            'price': float(p.price),
            'description': p.description,
            'image': p.image
        })

    role_label = 'Administrador' if is_user_admin(current_user) else 'Usuario'

    return render_template(
    'users.html',
    user=current_user,
    username=getattr(current_user, 'nameUser', getattr(current_user, 'username', 'Usuario')),
    products=products,
    orders_count=0,
    points=100,
    role_label=role_label
)

# 🔸 Editar perfil
@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        nameUser = request.form.get('nameUser')
        emailUser = request.form.get('emailUser')

        if not nameUser or not emailUser:
            flash('Por favor completa todos los campos', 'danger')
            return render_template('edit_profile.html', user=current_user)

        try:
            existing_user = User.query.filter(
                User.emailUser == emailUser,
                User.idUser != getattr(current_user, 'idUser', getattr(current_user, 'id', None))
            ).first()
        except Exception:
            existing_user = User.query.filter_by(emailUser=emailUser).first()
            if existing_user:
                existing_id = getattr(existing_user, 'idUser', getattr(existing_user, 'id', None))
                current_id = getattr(current_user, 'idUser', getattr(current_user, 'id', None))
                if existing_id == current_id:
                    existing_user = None

        if existing_user:
            flash('Este email ya está en uso por otro usuario', 'danger')
            return render_template('edit_profile.html', user=current_user)

        try:
            if hasattr(current_user, 'nameUser'):
                current_user.nameUser = nameUser
            elif hasattr(current_user, 'name'):
                current_user.name = nameUser

            if hasattr(current_user, 'emailUser'):
                current_user.emailUser = emailUser
            elif hasattr(current_user, 'email'):
                current_user.email = emailUser

            db.session.commit()
            flash('Perfil actualizado correctamente', 'success')
            return redirect(url_for('users.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error actualizando perfil: {e}', 'danger')
            return render_template('edit_profile.html', user=current_user)

    return render_template('edit_profile.html', user=current_user)


# 🔸 Cambiar contraseña
@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not current_password or not new_password or not confirm_password:
            flash('Por favor completa todos los campos', 'danger')
            return render_template('change_password.html')

        if new_password != confirm_password:
            flash('Las contraseñas nuevas no coinciden', 'danger')
            return render_template('change_password.html')

        try:
            if hasattr(current_user, 'check_password') and callable(getattr(current_user, 'check_password')):
                ok = current_user.check_password(current_password)
            else:
                ok = check_password_hash(getattr(current_user, 'password_hash', ''), current_password)
        except Exception:
            ok = False

        if not ok:
            flash('La contraseña actual es incorrecta', 'danger')
            return render_template('change_password.html')

        try:
            if hasattr(current_user, 'set_password') and callable(getattr(current_user, 'set_password')):
                current_user.set_password(new_password)
            else:
                current_user.password_hash = generate_password_hash(new_password)

            db.session.commit()
            flash('Contraseña actualizada correctamente', 'success')
            return redirect(url_for('users.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar contraseña: {e}', 'danger')
            return render_template('change_password.html')

    return render_template('change_password.html')


# 🔸 Listar productos (opcional)
@bp.route('/productos')
def productos():
    categoria = request.args.get('categoria')

    try:
        productos_db = Productos.query.all()
    except Exception:
        productos_db = []

    if categoria:
        productos_filtrados = [p for p in productos_db if p.category == categoria]
    else:
        productos_filtrados = productos_db

    categorias = list(set([p.category for p in productos_db]))

    return render_template(
        'users/productos.html',
        productos=productos_filtrados,
        categorias=categorias,
        categoria_seleccionada=categoria
    )

