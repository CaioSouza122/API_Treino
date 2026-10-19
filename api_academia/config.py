import os
from dotenv import load_dotenv

# Define base directory relative to config.py
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
ENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=ENV_PATH, encoding='latin-1')


class Config:
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = os.getenv('FLASK_TESTING', 'False').lower() == 'true'

    # API credentials
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    API_AUTH_KEY = os.getenv('API_AUTH_KEY')

    # CORS Security
    # Comma-separated list of browser origins, e.g. "https://meusite.com,https://app.meusite.com"
    # Empty by default: this API is called server-to-server, so browsers get no CORS access.
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '')

    # Database
    # Standard SQLite path in the root of the project as a fallback,
    # or PostgreSQL if provided in the environment variables
    DEFAULT_DB_PATH = os.path.join(BASE_DIR, 'api_academia.db')

    raw_db_url = os.getenv('DATABASE_URL')

    # Render and Heroku sometimes pass 'postgres://', which SQLAlchemy needs as 'postgresql://'
    if raw_db_url:
        if raw_db_url.startswith("postgres://"):
            raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = raw_db_url
    else:
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{DEFAULT_DB_PATH}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Neon closes idle connections: test each pooled connection before reuse
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 300}

    @staticmethod
    def init_app(app):
        # We can perform additional configuration setup here if needed
        pass
