"""Application Factory pattern module for api_academia.

Initializes Flask extensions (CORS, Rate Limiter, SQLAlchemy) and registers route blueprints.
"""

from typing import Type
from flask import Flask, jsonify
from flask_cors import CORS
from .config import Config
from .database import db
from .limiter import limiter
from .routes import api_blueprint


def create_app(config_class: Type[Config] = Config) -> Flask:
    """Application factory to instantiate and configure the Flask app.

    Args:
        config_class: Configuration class containing environment settings.

    Returns:
        Flask: Fully configured Flask application instance.
    """
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_class)
    config_class.init_app(app)

    # Fail closed: outside debug/testing the API must never run without authentication
    api_key = app.config.get('API_AUTH_KEY') or ''
    if not api_key.strip() and not (app.config.get('DEBUG') or app.config.get('TESTING')):
        raise RuntimeError("API_AUTH_KEY é obrigatória em produção (defina FLASK_DEBUG=True só em desenvolvimento).")

    # Configure CORS only for explicitly allowed browser origins
    allowed_origins = [
        origin.strip() for origin in (app.config.get('ALLOWED_ORIGINS') or '').split(',') if origin.strip()
    ]
    if allowed_origins:
        CORS(app, resources={r"/*": {"origins": allowed_origins}})

    # Initialize extensions
    limiter.init_app(app)
    db.init_app(app)

    # Register root landing route for health & documentation guidance
    @app.route('/')
    def home():
        return jsonify({
            "nome": "API de Treinos com IA (Gemini 2.5 Flash)",
            "versao": "1.0.0",
            "status": "online",
            "mensagem": "Backend rodando com sucesso. Utilize os endpoints RESTful sob /api/v1/",
            "endpoints": {
                "health_check": "GET /api/v1/health",
                "criar_treino": "POST /api/v1/treino",
                "listar_treinos": "GET /api/v1/treinos",
                "obter_treino": "GET /api/v1/treino/<id>",
                "deletar_treino": "DELETE /api/v1/treino/<id>"
            },
            "documentacao": "Consulte o README.md para obter especificações de cURL e esquemas JSON."
        }), 200

    # Register API blueprint with V1 pathing
    app.register_blueprint(api_blueprint, url_prefix="/api/v1")

    # Auto-create database tables inside app context
    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()

    return app
