"""is_lawyer

Revision ID: 6713ccfcac91
Revises: 4127cc9e874a
Create Date: 2025-04-11 19:54:49.870560

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6713ccfcac91'
down_revision = '4127cc9e874a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_lawyer', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('users', 'is_lawyer')