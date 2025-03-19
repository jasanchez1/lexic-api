"""make user_id nullable for reviews

Revision ID: 9b844f870e4b
Revises: 6d62e486ef46
Create Date: 2025-03-19 10:57:11.548939

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b844f870e4b'
down_revision = '6d62e486ef46'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('reviews', 'user_id', nullable=True)

def downgrade() -> None:
    op.alter_column('reviews', 'user_id', nullable=False)