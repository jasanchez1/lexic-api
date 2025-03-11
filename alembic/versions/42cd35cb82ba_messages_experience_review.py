"""messages experience review

Revision ID: 42cd35cb82ba
Revises: f8a3d5e71234
Create Date: 2025-03-11 22:00:28.385959

"""
from alembic import op
import sqlalchemy as sa
import uuid
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '42cd35cb82ba'
down_revision = 'f8a3d5e71234'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create reviews table
    op.create_table(
        'reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('author', sa.String(), nullable=False),
        sa.Column('author_email', sa.String(), nullable=False),
        sa.Column('lawyer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lawyers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('is_hired', sa.Boolean(), default=False),
        sa.Column('is_anonymous', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True)
    )
    
    # Create education table
    op.create_table(
        'education',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('lawyer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lawyers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('institution', sa.String(), nullable=False),
        sa.Column('degree', sa.String(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('honors', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True)
    )
    
    # Create work_experience table
    op.create_table(
        'work_experience',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('lawyer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lawyers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('company', sa.String(), nullable=False),
        sa.Column('start_date', sa.String(), nullable=True),
        sa.Column('end_date', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True)
    )
    
    # Create achievements table
    op.create_table(
        'achievements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('lawyer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lawyers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('issuer', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True)
    )
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('lawyer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lawyers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('read', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True)
    )
    
    # Create calls table
    op.create_table(
        'calls',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('lawyer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lawyers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('completed', sa.Boolean(), default=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    op.drop_table('calls')
    op.drop_table('messages')
    op.drop_table('achievements')
    op.drop_table('work_experience')
    op.drop_table('education')
    op.drop_table('reviews')
