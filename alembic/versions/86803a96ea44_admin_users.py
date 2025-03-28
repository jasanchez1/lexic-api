"""admin users

Revision ID: 86803a96ea44
Revises: 4dd40d473f26
Create Date: 2025-03-26 20:04:42.022757

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86803a96ea44'
down_revision = '4dd40d473f26'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_admin", sa.Boolean(), nullable=False, server_default="false"))

def downgrade() -> None:
    op.drop_column("users", "is_admin")
