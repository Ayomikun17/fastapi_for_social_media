"""add last few columns to posts table

Revision ID: 0165f46e069b
Revises: cabe573ed444
Create Date: 2024-07-04 18:35:53.049343

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0165f46e069b"
down_revision: Union[str, None] = "cabe573ed444"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "posts",
        sa.Column(
            "published", 
            sa.Boolean(), 
            nullable=False, 
            server_default="TRUE"),
    )
    op.add_column(
        "posts",
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )
    pass


def downgrade():
    op.drop_column("posts", "published")
    op.drop_column("posts", "created_at")
    pass
