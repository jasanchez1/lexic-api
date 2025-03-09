"""categories

Revision ID: e945f1147489
Revises: 8ccf465d50a2
Create Date: 2025-03-09 10:49:08.956142

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision = 'e945f1147489'
down_revision = '8ccf465d50a2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the practice_area_categories table
    op.create_table(
        'practice_area_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True)
    )
    
    # Create an index on the slug field
    op.create_index(op.f('ix_practice_area_categories_slug'), 'practice_area_categories', ['slug'], unique=True)
    
    # Add category_id column to practice_areas
    op.add_column('practice_areas', sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_practice_areas_category_id_practice_area_categories',
        'practice_areas', 'practice_area_categories',
        ['category_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Drop the old category column (since we have no real data yet)
    op.drop_column('practice_areas', 'category')
    
    # Make the new category_id column not nullable
    op.alter_column('practice_areas', 'category_id', nullable=False)


def downgrade() -> None:
    # Add back the old category column
    op.add_column('practice_areas', sa.Column('category', sa.String(), nullable=True))
    
    # Make category_id nullable so we can populate category
    op.alter_column('practice_areas', 'category_id', nullable=True)
    
    # Drop the foreign key
    op.drop_constraint('fk_practice_areas_category_id_practice_area_categories', 'practice_areas', type_='foreignkey')
    
    # Drop the category_id column
    op.drop_column('practice_areas', 'category_id')
    
    # Drop the categories table
    op.drop_index(op.f('ix_practice_area_categories_slug'), table_name='practice_area_categories')
    op.drop_table('practice_area_categories')