"""user_id on reviews and messages

Revision ID: 0e785f8d573c
Revises: 75a409e5c2c2
Create Date: 2025-03-12 23:56:37.644884

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '0e785f8d573c'
down_revision = '75a409e5c2c2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add user_id column to messages and reviews tables
    """
    # Add user_id column to messages table
    op.add_column('messages', sa.Column('user_id', postgresql.UUID(as_uuid=True), 
                                        sa.ForeignKey('users.id', ondelete='CASCADE'), 
                                        nullable=False)) 
    # Add user_id column to reviews table
    op.add_column('reviews', sa.Column('user_id', postgresql.UUID(as_uuid=True), 
                                        sa.ForeignKey('users.id', ondelete='CASCADE'), 
                                        nullable=True))
    
    # Then make the columns not nullable
    op.alter_column('messages', 'user_id', nullable=False)
    op.alter_column('reviews', 'user_id', nullable=False)


def downgrade() -> None:
    """
    Remove user_id column from messages and reviews tables
    """
    op.drop_column('messages', 'user_id')
    op.drop_column('reviews', 'user_id')