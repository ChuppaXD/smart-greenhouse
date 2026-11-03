"""actuator_states

Revision ID: c8a71f2e4d6b
Revises: 84bfc731ee2e
Create Date: 2026-11-03 14:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "c8a71f2e4d6b"
down_revision: Union[str, Sequence[str], None] = "84bfc731ee2e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "actuator_states",
        sa.Column(
            "device_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "state",
            sa.String(length=32),
            server_default=sa.text("'idle'"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["devices.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("device_id"),
    )

    op.execute(
        sa.text(
            """
            INSERT INTO actuator_states (
                device_id,
                state,
                updated_at
            )
            SELECT
                id,
                'idle',
                now()
            FROM devices
            WHERE role = 'actuator'
            """
        )
    )


def downgrade() -> None:
    op.drop_table("actuator_states")