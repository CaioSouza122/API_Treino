"""DATABASE_URL normalization (Neon / Render URLs)."""

from api_academia.config import normalizar_database_url


def test_postgres_urls_pin_psycopg2_driver():
    neon = "postgresql://u:p@ep-x.neon.tech/neondb?sslmode=require"
    assert normalizar_database_url(neon) == "postgresql+psycopg2://u:p@ep-x.neon.tech/neondb?sslmode=require"
    assert normalizar_database_url("postgres://u:p@host/db") == "postgresql+psycopg2://u:p@host/db"


def test_other_urls_are_untouched():
    assert normalizar_database_url("sqlite:///C:/dados/x.db") == "sqlite:///C:/dados/x.db"
    assert normalizar_database_url("postgresql+psycopg2://u@h/db") == "postgresql+psycopg2://u@h/db"
    assert normalizar_database_url("") is None
    assert normalizar_database_url(None) is None
