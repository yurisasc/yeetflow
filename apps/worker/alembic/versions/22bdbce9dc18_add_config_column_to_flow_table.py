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

    # 4) Add indexes for performance on typical queries
    # Index for admin listing: flows ordered by created_at desc, id desc
    op.create_index("ix_flow_created_at_id", "flow", ["created_at", "id"])

    # Index for user listing: flows by user ordered by created_at desc, id desc
    op.create_index(
        "ix_flow_created_by_created_at_id", "flow", ["created_by", "created_at", "id"]
    )

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # Remove indexes added in upgrade
    op.drop_index("ix_flow_created_by_created_at_id", table_name="flow")
    op.drop_index("ix_flow_created_at_id", table_name="flow")

    # Remove config column
    with op.batch_alter_table("flow", schema=None) as batch_op:
        batch_op.drop_column("config")

    # ### end Alembic commands ###
