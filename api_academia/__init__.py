import os
from flask import Flask
from flask_cors import CORS
from .config import Config
from .database import db
from .limiter import limiter
from .routes import api_blueprint

def create_app(config_class=Config):
    """Application factory to create and configure the Flask app.
    
    Args:
        config_class: Configuration class to load settings from.
        
    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)
    
    # Load settings
    app.config.from_object(config_class)
    config_class.init_app(app)
    
    # Enable CORS so other projects (web frontends, mobile backends, etc.) can fetch from this API.
    # We load origins dynamically: either "*" or a specific list of domains from ALLOWED_ORIGINS.
    allowed_origins = app.config.get('ALLOWED_ORIGINS', '*')
    if ',' in allowed_origins:
        allowed_origins = [origin.strip() for origin in allowed_origins.split(',')]
        
    CORS(app, resources={r"/api/*": {"origins": allowed_origins}})
    
    # Initialize rate limiting to protect the server and API keys
    limiter.init_app(app)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprint with V1 pathing
    app.register_blueprint(api_blueprint, url_prefix="/api/v1")
    
    # Auto-create SQLite or PostgreSQL database tables if they do not exist
    with app.app_context():
        # Import models inside context to ensure they register correctly
        from . import models
        db.create_all()
        
    return app
