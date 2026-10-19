"""Alembic environment: same database URL and pool options as the Flask app."""

from alembic import context
from sqlalchemy import create_engine

from api_academia import models  # noqa: F401 - registers tables on the metadata
from api_academia.config import Config
from api_academia.database import db

# Own version table: the Neon database may be shared with the HIPERTROF.IA backend
VERSION_TABLE = "alembic_version_api_treino"
URL = Config.SQLALCHEMY_DATABASE_URI

if context.is_offline_mode():
    context.configure(url=URL, target_metadata=db.metadata, version_table=VERSION_TABLE)
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = create_engine(URL, pool_pre_ping=True)
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=db.metadata,
            version_table=VERSION_TABLE,
            render_as_batch=connection.dialect.name == "sqlite",
        )
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()
