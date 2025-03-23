"""category migration

Revision ID: 2c25ef3a4ae3
Revises: 47661c5ea989
Create Date: 2025-03-23 21:14:24.169705

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision = "2c25ef3a4ae3"
down_revision = "47661c5ea989"
branch_labels = None
depends_on = None


def upgrade():
    # Create guide_categories table
    op.create_table(
        "guide_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create index on slug
    op.create_index("ix_guide_categories_slug", "guide_categories", ["slug"], unique=True)
    
    # Add category_id column to guides table
    op.add_column("guides", sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True))
    
    # Add foreign key
    op.create_foreign_key(
        "fk_guides_category_id_guide_categories",
        "guides", "guide_categories",
        ["category_id"], ["id"],
        ondelete="SET NULL"
    )
    
    # Data migration: create guide categories and update guides
    # This needs to be run in a transaction
    conn = op.get_bind()
    
    # Get unique category names and slugs from guides table
    result = conn.execute(
        sa.text("SELECT DISTINCT category_name, category_slug FROM guides WHERE category_name IS NOT NULL AND category_slug IS NOT NULL")
    ).fetchall()
    
    # Insert categories into guide_categories table
    for name, slug in result:
        # Generate a UUID for the category
        category_id = uuid.uuid4()
        
        # Insert into guide_categories
        conn.execute(
            sa.text("INSERT INTO guide_categories (id, name, slug, created_at, updated_at) VALUES (:id, :name, :slug, NOW(), NOW())"),
            {"id": category_id, "name": name, "slug": slug}
        )
        
        # Update guides with this category
        conn.execute(
            sa.text("UPDATE guides SET category_id = :category_id WHERE category_slug = :slug"),
            {"category_id": category_id, "slug": slug}
        )


def downgrade():
    # Drop foreign key constraint
    op.drop_constraint("fk_guides_category_id_guide_categories", "guides", type_="foreignkey")
    
    # Drop category_id column from guides
    op.drop_column("guides", "category_id")
    
    # Drop guide_categories table
    op.drop_index("ix_guide_categories_slug", table_name="guide_categories")
    op.drop_table("guide_categories")