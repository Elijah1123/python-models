import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate

from app.config import config

# Extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()

# JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired', 'message': 'Please log in again'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'error': 'Invalid token', 'message': 'Please provide a valid token'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'error': 'Authorization required', 'message': 'Please include your access token'}), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has been revoked', 'message': 'Please log in again'}), 401

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Import and register blueprints (absolute imports!)
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.payments import payments_bp
    from app.routes.main import main_bp
    from app.routes.breweries import breweries_bp
    from app.routes.tours import tours_bp
    from app.routes.bookings import bookings_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(breweries_bp, url_prefix='/api/breweries')
    app.register_blueprint(tours_bp, url_prefix='/api/tours')
    app.register_blueprint(bookings_bp, url_prefix='/api/bookings')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')

    # Create upload directories if not exist
    upload_dirs = [
        'static/uploads/breweries',
        'static/uploads/tours',
        'static/uploads/users'
    ]
    for directory in upload_dirs:
        os.makedirs(os.path.join(app.root_path, directory), exist_ok=True)

    return app
