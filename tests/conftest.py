"""Pytest fixtures for API_Treino test suite.

Configures an isolated application context using an in-memory SQLite database
and mocks external AI services (Google GenAI Gemini API) to guarantee test reliability.
"""

import pytest
from typing import Generator
from flask import Flask
from flask.testing import FlaskClient

from api_academia import create_app
from api_academia.config import Config
from api_academia.database import db


class TestConfig(Config):
    """Testing configuration overriding database and security flags."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    RATELIMIT_ENABLED = False
    GEMINI_API_KEY = "test_gemini_api_key_mock"
    API_AUTH_KEY = "test_secret_api_key"
    ALLOWED_ORIGINS = ""  # isolate tests from whatever the local .env sets


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    """Creates and configures a new Flask application instance for each test."""
    _app = create_app(TestConfig)

    with _app.app_context():
        db.create_all()
        yield _app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """A test client for sending HTTP requests to the application."""
    return app.test_client()


@pytest.fixture
def auth_headers() -> dict:
    """Standard HTTP headers including the valid X-API-KEY."""
    return {
        'Content-Type': 'application/json',
        'X-API-KEY': 'test_secret_api_key'
    }


@pytest.fixture
def mock_gemini(mocker) -> Generator:
    """Mocks the generate_treino service function to prevent external API calls during tests."""
    mock_service = mocker.patch(
        'api_academia.routes.generate_treino',
        return_value=(
            "### Treino de Teste Gerado via Mock IA\n\n"
            "1. **Agachamento Livre** - 4 séries de 10 repetições\n"
            "2. **Leg Press 45** - 3 séries de 12 repetições\n"
            "3. **Cadeira Extensora** - 3 séries de 15 repetições"
        )
    )
    yield mock_service
