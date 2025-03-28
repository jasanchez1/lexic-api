"""conversations

Revision ID: 4127cc9e874a
Revises: 86803a96ea44
Create Date: 2025-03-28 17:17:51.050619

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision = '4127cc9e874a'
down_revision = '86803a96ea44'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('lawyer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lawyers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('last_message', sa.Text(), nullable=True),
        sa.Column('last_message_date', sa.DateTime(), nullable=True),
        sa.Column('unread_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True)
    )
    
    # Create conversation_messages table
    op.create_table(
        'conversation_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('from_lawyer', sa.Boolean(), default=False),
        sa.Column('read', sa.Boolean(), default=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True)
    )
    
    # Create indices for better performance
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('ix_conversations_lawyer_id', 'conversations', ['lawyer_id'])
    op.create_index('ix_conversations_last_message_date', 'conversations', ['last_message_date'])
    op.create_index('ix_conversation_messages_conversation_id', 'conversation_messages', ['conversation_id'])
    op.create_index('ix_conversation_messages_timestamp', 'conversation_messages', ['timestamp'])


def downgrade() -> None:
    # Drop tables and indexes
    op.drop_index('ix_conversation_messages_timestamp', table_name='conversation_messages')
    op.drop_index('ix_conversation_messages_conversation_id', table_name='conversation_messages')
    op.drop_table('conversation_messages')
    op.drop_index('ix_conversations_last_message_date', table_name='conversations')
    op.drop_index('ix_conversations_lawyer_id', table_name='conversations')
    op.drop_index('ix_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')