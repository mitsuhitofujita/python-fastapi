"""add cities table

Revision ID: ea788c0b8b4a
Revises: 12824e5c484c
Create Date: 2025-11-09 09:01:13.867056

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ea788c0b8b4a"
down_revision: str | Sequence[str] | None = "12824e5c484c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create cities table
    op.create_table(
        "cities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("state_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["state_id"], ["main.states.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        schema="main",
    )

    # Create conditional unique index: code is unique only when is_active = true
    op.create_index(
        "cities_code_active_unique",
        "cities",
        ["code"],
        unique=True,
        schema="main",
        postgresql_where=sa.text("is_active = true"),
    )

    # Create index on state_id for faster foreign key lookups
    op.create_index("idx_cities_state_id", "cities", ["state_id"], schema="main")

    # Create index on is_active for filtering queries
    op.create_index("idx_cities_is_active", "cities", ["is_active"], schema="main")


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes on cities table
    op.drop_index("idx_cities_is_active", table_name="cities", schema="main")
    op.drop_index("idx_cities_state_id", table_name="cities", schema="main")
    op.drop_index("cities_code_active_unique", table_name="cities", schema="main")

    # Drop cities table
    op.drop_table("cities", schema="main")
