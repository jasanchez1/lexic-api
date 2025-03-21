"""make userr_id nullable in questions

Revision ID: 501b6e54466a
Revises: 9b844f870e4b
Create Date: 2025-03-21 20:47:39.529653

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '501b6e54466a'
down_revision = '9b844f870e4b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('questions', 'user_id', nullable=True)

def downgrade() -> None:
    op.alter_column('questions', 'user_id', nullable=False)