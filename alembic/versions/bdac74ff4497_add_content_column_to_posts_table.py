"""add content column to posts table

Revision ID: bdac74ff4497
Revises: 81b673acf4a8
Create Date: 2024-07-04 18:14:29.416525

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bdac74ff4497'
down_revision: Union[str, None] = '81b673acf4a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('posts',sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_column('posts','content')
    pass
