"""documents

Revision ID: 399e987821c8
Revises: 6713ccfcac91
Create Date: 2025-05-17 19:02:53.374142

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision = '399e987821c8'
down_revision = '6713ccfcac91'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add verification_status column to lawyers table
    op.add_column('lawyers', 
                  sa.Column('verification_status', 
                            sa.String(20), 
                            nullable=False, 
                            server_default='pending'))
    
    # Add check constraint to verification_status
    op.create_check_constraint(
        'verification_status_check',
        'lawyers',
        sa.column('verification_status').in_(['pending', 'partial', 'verified', 'rejected'])
    )
    
    # Create lawyer_documents table
    op.create_table(
        'lawyer_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('lawyer_id', postgresql.UUID(as_uuid=True), 
                  sa.ForeignKey('lawyers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('document_type', sa.String(50), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(512), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending_review'),
        sa.Column('upload_date', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('review_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('users.id'), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
    )
    
    # Add check constraint to document_type
    op.create_check_constraint(
        'document_type_check',
        'lawyer_documents',
        sa.column('document_type').in_(['supreme_court_certificate', 'university_degree'])
    )
    
    # Add check constraint to status
    op.create_check_constraint(
        'document_status_check',
        'lawyer_documents',
        sa.column('status').in_(['pending_review', 'approved', 'rejected'])
    )
    
    # Add unique constraint for lawyer_id and document_type
    op.create_unique_constraint(
        'lawyer_documents_lawyer_id_document_type_key',
        'lawyer_documents',
        ['lawyer_id', 'document_type']
    )
    
    # Add index on lawyer_id for better performance
    op.create_index('idx_lawyer_documents_lawyer_id', 'lawyer_documents', ['lawyer_id'])


def downgrade() -> None:
    # Drop the lawyer_documents table and all related constraints
    op.drop_index('idx_lawyer_documents_lawyer_id', table_name='lawyer_documents')
    op.drop_constraint('lawyer_documents_lawyer_id_document_type_key', 'lawyer_documents')
    op.drop_constraint('document_status_check', 'lawyer_documents')
    op.drop_constraint('document_type_check', 'lawyer_documents')
    op.drop_table('lawyer_documents')
    
    # Drop the verification_status column constraint
    op.drop_constraint('verification_status_check', 'lawyers')
    
    # Drop the verification_status column
    op.drop_column('lawyers', 'verification_status')