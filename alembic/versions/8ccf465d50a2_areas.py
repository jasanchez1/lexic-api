"""areas

Revision ID: 8ccf465d50a2
Revises: c298899ed153
Create Date: 2025-03-08 21:35:52.933502

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '8ccf465d50a2'
down_revision = 'c298899ed153'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create practice_areas table
    op.create_table(
        'practice_areas',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add index to slug field
    op.create_index(op.f('ix_practice_areas_slug'), 'practice_areas', ['slug'], unique=True)
    
    # Create lawyers table (for the lawyer model we'll build next)
    op.create_table(
        'lawyers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('languages', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True, default=False),
        sa.Column('professional_start_date', sa.DateTime(), nullable=True),
        sa.Column('catchphrase', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index(op.f('ix_lawyers_email'), 'lawyers', ['email'], unique=True)
    
    # Create lawyer_areas association table
    op.create_table(
        'lawyer_areas',
        sa.Column('lawyer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('area_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('experience_score', sa.Integer(), nullable=True, default=0),
        sa.ForeignKeyConstraint(['lawyer_id'], ['lawyers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['area_id'], ['practice_areas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('lawyer_id', 'area_id')
    )


def downgrade() -> None:
    op.drop_table('lawyer_areas')
    op.drop_index(op.f('ix_lawyers_email'), table_name='lawyers')
    op.drop_table('lawyers')
    op.drop_index(op.f('ix_practice_areas_slug'), table_name='practice_areas')
    op.drop_table('practice_areas')