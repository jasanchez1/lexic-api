"""review count

Revision ID: 75a409e5c2c2
Revises: 42cd35cb82ba
Create Date: 2025-03-12 19:49:37.113935

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75a409e5c2c2'
down_revision = '42cd35cb82ba'
branch_labels = None
depends_on = None


def upgrade() -> None:
    "adds review count and score column to lawyers table"
    op.add_column('lawyers', sa.Column('review_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('lawyers', sa.Column('review_score', sa.Float(), nullable=False, server_default='0.0'))

def downgrade() -> None:
    "removes review count and score column from lawyers table"
    op.drop_column('lawyers', 'review_score')
    op.drop_column('lawyers', 'review_count')