"""guides and analytics

Revision ID: 6d62e486ef46
Revises: 0e785f8d573c
Create Date: 2025-03-18 13:41:33.161656

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision = "6d62e486ef46"
down_revision = "0e785f8d573c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create guide tables
    op.create_table(
        "guides",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("published", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "guide_sections",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column(
            "guide_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("guides.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("section_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("display_order", sa.Integer(), default=0),
        sa.Column("always_open", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "guide_related_guides",
        sa.Column(
            "guide_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("guides.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "related_guide_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("guides.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    # Create analytics tables

    # Profile Views
    op.create_table(
        "profile_views",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column(
            "lawyer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lawyers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("source", sa.String(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "profile_view_counts",
        sa.Column(
            "lawyer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lawyers.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("count", sa.Integer(), default=0),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # Message Events
    op.create_table(
        "message_events",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column(
            "lawyer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lawyers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "message_event_counts",
        sa.Column(
            "lawyer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lawyers.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("status", sa.String(), primary_key=True),
        sa.Column("count", sa.Integer(), default=0),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # Call Events
    op.create_table(
        "call_events",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column(
            "lawyer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lawyers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("completed", sa.Boolean(), default=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "call_event_counts",
        sa.Column(
            "lawyer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lawyers.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("count", sa.Integer(), default=0),
        sa.Column("completed_count", sa.Integer(), default=0),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # Profile Impressions
    op.create_table(
        "profile_impressions",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column(
            "lawyer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lawyers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("search_query", sa.String(), nullable=True),
        sa.Column("area_slug", sa.String(), nullable=True),
        sa.Column("city_slug", sa.String(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "profile_impression_counts",
        sa.Column(
            "lawyer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lawyers.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("count", sa.Integer(), default=0),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # Listing Clicks
    op.create_table(
        "listing_clicks",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column(
            "lawyer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lawyers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("search_query", sa.String(), nullable=True),
        sa.Column("area_slug", sa.String(), nullable=True),
        sa.Column("city_slug", sa.String(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "listing_click_counts",
        sa.Column(
            "lawyer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lawyers.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("count", sa.Integer(), default=0),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # Guide Views
    op.create_table(
        "guide_views",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column(
            "guide_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("guides.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "guide_view_counts",
        sa.Column(
            "guide_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("guides.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("count", sa.Integer(), default=0),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # Question Views
    op.create_table(
        "question_views",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
        ),
        sa.Column(
            "question_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("questions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "question_view_counts",
        sa.Column(
            "question_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("questions.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("count", sa.Integer(), default=0),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # Populate guide data with initial guides
    op.execute(
        f"""
    INSERT INTO guides (id, title, slug, description, published, created_at, updated_at)
    VALUES 
        ('{str(uuid.uuid4())}', 'Posesión Efectiva en Chile', 'posesion-efectiva-chile', 'Guía completa sobre el proceso de posesión efectiva en Chile', TRUE, NOW(), NOW()),
        ('{str(uuid.uuid4())}', 'Alzamiento de Hipotecas en Chile', 'alzamiento-hipotecas-chile', 'Todo lo que necesitas saber sobre el alzamiento de hipotecas en Chile', TRUE, NOW(), NOW()),
        ('{str(uuid.uuid4())}', 'Cambio de Nombre y Apellido en Chile', 'cambio-nombre-apellido-chile', 'Procedimiento para cambiar tu nombre y/o apellido en Chile', TRUE, NOW(), NOW())
    """
    )

    # Set up related guides relationships
    op.execute(
        """
    -- Link Posesión Efectiva with related guides
    INSERT INTO guide_related_guides (guide_id, related_guide_id)
    SELECT g1.id, g2.id
    FROM guides g1, guides g2
    WHERE g1.slug = 'posesion-efectiva-chile' AND g2.slug = 'alzamiento-hipotecas-chile';
    
    INSERT INTO guide_related_guides (guide_id, related_guide_id)
    SELECT g1.id, g2.id
    FROM guides g1, guides g2
    WHERE g1.slug = 'posesion-efectiva-chile' AND g2.slug = 'cambio-nombre-apellido-chile';
    
    -- Link Alzamiento de Hipotecas with related guides
    INSERT INTO guide_related_guides (guide_id, related_guide_id)
    SELECT g1.id, g2.id
    FROM guides g1, guides g2
    WHERE g1.slug = 'alzamiento-hipotecas-chile' AND g2.slug = 'posesion-efectiva-chile';
    
    INSERT INTO guide_related_guides (guide_id, related_guide_id)
    SELECT g1.id, g2.id
    FROM guides g1, guides g2
    WHERE g1.slug = 'alzamiento-hipotecas-chile' AND g2.slug = 'cambio-nombre-apellido-chile';
    
    -- Link Cambio de Nombre with related guides
    INSERT INTO guide_related_guides (guide_id, related_guide_id)
    SELECT g1.id, g2.id
    FROM guides g1, guides g2
    WHERE g1.slug = 'cambio-nombre-apellido-chile' AND g2.slug = 'posesion-efectiva-chile';
    
    INSERT INTO guide_related_guides (guide_id, related_guide_id)
    SELECT g1.id, g2.id
    FROM guides g1, guides g2
    WHERE g1.slug = 'cambio-nombre-apellido-chile' AND g2.slug = 'alzamiento-hipotecas-chile';
    """
    )


def downgrade() -> None:
    # Drop all analytics and guide tables

    # First drop tables with foreign keys to avoid constraint issues

    # Question Views
    op.drop_table("question_view_counts")
    op.drop_table("question_views")

    # Guide Views
    op.drop_table("guide_view_counts")
    op.drop_table("guide_views")

    # Listing Clicks
    op.drop_table("listing_click_counts")
    op.drop_table("listing_clicks")

    # Profile Impressions
    op.drop_table("profile_impression_counts")
    op.drop_table("profile_impressions")

    # Call Events
    op.drop_table("call_event_counts")
    op.drop_table("call_events")

    # Message Events
    op.drop_table("message_event_counts")
    op.drop_table("message_events")

    # Profile Views
    op.drop_table("profile_view_counts")
    op.drop_table("profile_views")

    # Guide tables
    op.drop_table("guide_related_guides")
    op.drop_table("guide_sections")
    op.drop_table("guides")
