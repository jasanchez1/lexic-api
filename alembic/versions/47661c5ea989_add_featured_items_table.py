"""add featured items table

Revision ID: 47661c5ea989
Revises: 501b6e54466a
Create Date: 2025-03-22 10:57:10.999496

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "47661c5ea989"
down_revision = "501b6e54466a"
branch_labels = None
depends_on = None


def upgrade():
    # Create featured_items table
    op.create_table(
        "featured_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("item_type", sa.String(), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("display_order", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now()),
        sa.Column(
            "updated_at", sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()
        ),
    )

    # Add index on item_type for faster filtering
    op.create_index("ix_featured_items_item_type", "featured_items", ["item_type"])

    # Add index on parent_id for faster filtering
    op.create_index("ix_featured_items_parent_id", "featured_items", ["parent_id"])

    # Add index on display_order for faster sorting
    op.create_index(
        "ix_featured_items_display_order", "featured_items", ["display_order"]
    )

    # Add guide category fields to guides table
    op.add_column("guides", sa.Column("category_name", sa.String(), nullable=True))
    op.add_column("guides", sa.Column("category_slug", sa.String(), nullable=True))

    # Add index on category_slug for faster filtering
    op.create_index("ix_guides_category_slug", "guides", ["category_slug"])


def downgrade():
    # Drop indexes
    op.drop_index("ix_featured_items_item_type")
    op.drop_index("ix_featured_items_parent_id")
    op.drop_index("ix_featured_items_display_order")
    op.drop_index("ix_guides_category_slug")

    # Drop columns from guides table
    op.drop_column("guides", "category_name")
    op.drop_column("guides", "category_slug")

    # Drop featured_items table
    op.drop_table("featured_items")
