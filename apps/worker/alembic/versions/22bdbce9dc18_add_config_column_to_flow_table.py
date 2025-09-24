"""add config column to flow table

Revision ID: 22bdbce9dc18
Revises: 02c49f2fa2ea
Create Date: 2025-09-23 11:43:01.426042

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "22bdbce9dc18"
down_revision: str | Sequence[str] | None = "02c49f2fa2ea"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1) Add column as nullable, generic JSON
    with op.batch_alter_table("flow", schema=None) as batch_op:
        batch_op.add_column(sa.Column("config", sa.JSON(), nullable=True))

    # 2) Backfill existing rows with empty object
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == "postgresql":
        op.execute("UPDATE flow SET config = '{}'::jsonb WHERE config IS NULL")
    else:
        # SQLite/MySQL
        op.execute("UPDATE flow SET config = '{}' WHERE config IS NULL")

    # 3) Enforce NOT NULL
    with op.batch_alter_table("flow", schema=None) as batch_op:
        batch_op.alter_column("config", existing_type=sa.JSON(), nullable=False)

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("run", schema=None) as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.VARCHAR(length=14),
            server_default=sa.text("'pending'"),
            existing_nullable=False,
        )

    # ### end Alembic commands ###
