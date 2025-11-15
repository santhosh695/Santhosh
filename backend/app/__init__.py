from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from config import config_by_name

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
cors = CORS()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Disable CSRF for development
    if app.config['DEBUG']:
        print("🔓 CSRF protection disabled for development")
    else:
        csrf.init_app(app,
                      origins=app.config['CORS_ORIGINS'],
                      methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
                      allow_headers=['Content-Type', 'Authorization'],
                      supports_credentials=True)

    cors.init_app(app,
                  origins=app.config['CORS_ORIGINS'],
                  methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
                  allow_headers=['Content-Type', 'Authorization'],
                  supports_credentials=True)

    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.fir import fir_bp
    from app.routes.legal import legal_bp
    from app.routes.public import public_bp
    from app.routes.upload import upload_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(fir_bp, url_prefix='/api/police')
    app.register_blueprint(legal_bp, url_prefix='/api/legal')
    app.register_blueprint(public_bp, url_prefix='/api/public')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')

    # Create upload folder if it doesn't exist
    import os
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Resource not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return {'error': 'Access forbidden'}, 403

    @app.errorhandler(401)
    def unauthorized_error(error):
        return {'error': 'Unauthorized'}, 401

    # Simple test endpoint
    @app.route('/api/test', methods=['GET'])
    def simple_test():
        return {
            'success': True,
            'message': 'Backend is working!',
            'cors': 'fixed'
        }

    # Simple registration test endpoint
    @app.route('/api/register-test', methods=['POST'])
    def register_test():
        try:
            data = request.get_json()
            return {
                'success': True,
                'message': 'Registration data received',
                'data': data,
                'received_fields': list(data.keys()) if data else []
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    # Health check endpoint for deployment services
    @app.route('/api/health')
    def health_check():
        return {
            'status': 'healthy',
            'message': 'Law Mate API is running',
            'version': '1.0.0',
            'features': {
                'authentication': True,
                'fir_management': True,
                'complaint_writing': True,
                'legal_search': True,
                'subscriptions': False,
                'payments': False
            }
        }

    # Add CORS headers to all responses
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        return response

    return app