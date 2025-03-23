"""drop category columns from guides

Revision ID: 4dd40d473f26
Revises: 2c25ef3a4ae3
Create Date: 2025-03-23 22:03:19.232972

"""
from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision = '4dd40d473f26'
down_revision = '2c25ef3a4ae3'
branch_labels = None
depends_on = None


def upgrade():
    # Ensure all guides are using category_id instead of the legacy fields
    conn = op.get_bind()
    
    # Find guides that have category_slug but not category_id
    result = conn.execute(
        sa.text("""
            SELECT id, category_name, category_slug 
            FROM guides 
            WHERE category_slug IS NOT NULL
            AND category_id IS NULL
        """)
    ).fetchall()
    
    # For each such guide, find the corresponding category_id
    for guide_id, category_name, category_slug in result:
        # Find the category by slug
        category = conn.execute(
            sa.text("SELECT id FROM guide_categories WHERE slug = :slug"),
            {"slug": category_slug}
        ).fetchone()
        
        if category:
            # Update the guide with the category_id
            conn.execute(
                sa.text("UPDATE guides SET category_id = :category_id WHERE id = :guide_id"),
                {"category_id": category[0], "guide_id": guide_id}
            )
        else:
            # Create the category if it doesn't exist
            category_id = uuid.uuid4()
            conn.execute(
                sa.text("INSERT INTO guide_categories (id, name, slug, created_at, updated_at) VALUES (:id, :name, :slug, NOW(), NOW())"),
                {"id": category_id, "name": category_name, "slug": category_slug}
            )
            
            # Update the guide with the new category_id
            conn.execute(
                sa.text("UPDATE guides SET category_id = :category_id WHERE id = :guide_id"),
                {"category_id": category_id, "guide_id": guide_id}
            )
    
    # Now drop the legacy columns
    op.drop_index("ix_guides_category_slug", table_name="guides")
    op.drop_column("guides", "category_name")
    op.drop_column("guides", "category_slug")


def downgrade():
    # Add back the legacy columns
    op.add_column("guides", sa.Column("category_name", sa.String(), nullable=True))
    op.add_column("guides", sa.Column("category_slug", sa.String(), nullable=True))
    op.create_index("ix_guides_category_slug", "guides", ["category_slug"])
    
    # Restore the legacy column values
    conn = op.get_bind()
    
    # Find guides with category_id
    result = conn.execute(
        sa.text("""
            SELECT g.id, g.category_id, c.name, c.slug
            FROM guides g
            JOIN guide_categories c ON g.category_id = c.id
            WHERE g.category_id IS NOT NULL
        """)
    ).fetchall()
    
    # Update the legacy columns
    for guide_id, category_id, name, slug in result:
        conn.execute(
            sa.text("""
                UPDATE guides
                SET category_name = :name,
                    category_slug = :slug
                WHERE id = :guide_id
            """),
            {"name": name, "slug": slug, "guide_id": guide_id}
        )