from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
# ✅ ELIMINADA la importación circular: from app.models import Product
import os



# Importar la configuración
from config import Config

# Inicializar extensiones PRIMERO
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # 🔒 Cargar configuración desde la clase Config (que usa variables de entorno)
    app.config.from_object(Config)
    
    
    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    
    # Configurar Login Manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    
    # Importar y configurar user_loader DENTRO de create_app
    from app.models.usuarios import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # ✅ CORREGIDO: Crear tablas pero NO crear admin todavía (por el problema de created_at)
    with app.app_context():
        db.create_all()
        
        # Print para depurar la URI de DB cargada
        print(f"URI de DB cargada: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # ✅ SOLUCIÓN: Verificar si la columna created_at existe antes de crear el admin
        try:
            admin_user = db.session.query(User).filter_by(emailUser='admin@fashion.com').first()
            if not admin_user:
                admin = User(
                    nameUser='admin',
                    emailUser='admin@fashion.com',
                    is_admin=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✅ Administrador creado: admin@fashion.com / admin123")
        except Exception as e:
            print(f"⚠️  No se pudo crear el admin: {e}")
            print("💡 Ejecuta: flask db migrate && flask db upgrade")
    
    # ✅ RUTA PRINCIPAL - Página de inicio con todos los productos
    @app.route('/')
    def index():
        # ✅ IMPORTAR Product DENTRO de la función para evitar circular import
        from app.models.products import Productos
        
        page = request.args.get('page', 1, type=int)
        per_page = 30  # ✅ 30 productos por página (no 6)
        
        # Obtener productos con paginación
        products_query = Productos.query.filter_by(status='Activo')
        pagination = products_query.paginate(
            page=page, 
            per_page=per_page,
            error_out=False
        )
        
        products = pagination.items
        
        # Convertir productos a formato para la template
        products_data = []
        for product in products:
            products_data.append({
                'id': product.idProduct,
                'name': product.nameProduct,
                'description': product.description or '',
                'price': float(product.price),
                'image_url': product.image or f'https://via.placeholder.com/300x400/f8f9fa/000?text={product.nameProduct}',
                'category': product.category,
                'stock': product.stock,
                'status': product.status
            })
        
        return render_template('index.html', 
                             products=products_data,
                             current_page=page,
                             total_pages=pagination.pages,
                             has_next=pagination.has_next,
                             has_prev=pagination.has_prev)
    
    # ✅ VERIFICAR QUE products_bp ESTÉ REGISTRADO SIN url_prefix
    # Registrar blueprints
    from app.routes.auth import bp as auth_bp
    from app.routes.users_route import bp as users_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.products import products_bp
    #from app.routes.cart import cart_bp
    from app.routes.pedidos import pedidos_bp
    from app.routes.reportes import reportes_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(dashboard_bp)
    
    # ✅ PUNTO 2 CRÍTICO: Asegurar que products_bp esté registrado SIN url_prefix
    # Esto permite que la ruta '/' en products.py funcione correctamente
    app.register_blueprint(products_bp)  # SIN url_prefix - para que maneje '/'
    
    app.register_blueprint(pedidos_bp)
    #app.register_blueprint(cart_bp)
    app.register_blueprint(reportes_bp)
    
    return app