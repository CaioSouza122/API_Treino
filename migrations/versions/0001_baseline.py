"""Baseline: treinos table.

Idempotent: databases that already have the table (created by db.create_all)
become versioned without errors or data loss.

Revision ID: 0001_baseline
Revises:
Create Date: 2026-10-19
"""

import sqlalchemy as sa
from alembic import op

revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    if sa.inspect(op.get_bind()).has_table("treinos"):
        return
    op.create_table(
        "treinos",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("objetivo", sa.String(length=255), nullable=False),
        sa.Column("nivel", sa.String(length=50), nullable=False),
        sa.Column("treino_gerado", sa.Text(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("treinos")
