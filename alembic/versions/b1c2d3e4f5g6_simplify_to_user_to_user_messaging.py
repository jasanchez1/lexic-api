"""simplify to user-to-user messaging

Revision ID: b1c2d3e4f5g6
Revises: 4f400c93279a
Create Date: 2025-07-19 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'b1c2d3e4f5g6'
down_revision = '4f400c93279a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # NUKE EVERYTHING - start completely fresh
    op.execute("DELETE FROM conversation_messages")
    op.execute("DELETE FROM conversations")
    
    # Drop old conversation_messages table
    op.drop_table('conversation_messages')
    
    # Drop old conversations table
    op.drop_table('conversations')
    
    # Create new simplified conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('participant_1_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('participant_2_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('last_message', sa.Text(), nullable=True),
        sa.Column('last_message_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    
    # Create new simplified conversation_messages table
    op.create_table(
        'conversation_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sender_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('read', sa.Boolean(), default=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    
    # Create indices for performance
    op.create_index('ix_conversations_participant_1_id', 'conversations', ['participant_1_id'])
    op.create_index('ix_conversations_participant_2_id', 'conversations', ['participant_2_id'])
    op.create_index('ix_conversations_last_message_date', 'conversations', ['last_message_date'])
    op.create_index('ix_conversation_messages_conversation_id', 'conversation_messages', ['conversation_id'])
    op.create_index('ix_conversation_messages_sender_id', 'conversation_messages', ['sender_id'])
    op.create_index('ix_conversation_messages_timestamp', 'conversation_messages', ['timestamp'])


def downgrade() -> None:
    # Drop new tables and indexes
    op.drop_index('ix_conversation_messages_timestamp', table_name='conversation_messages')
    op.drop_index('ix_conversation_messages_sender_id', table_name='conversation_messages')
    op.drop_index('ix_conversation_messages_conversation_id', table_name='conversation_messages')
    op.drop_table('conversation_messages')
    
    op.drop_index('ix_conversations_last_message_date', table_name='conversations')
    op.drop_index('ix_conversations_participant_2_id', table_name='conversations')
    op.drop_index('ix_conversations_participant_1_id', table_name='conversations')
    op.drop_table('conversations')
    
    # Recreate old tables (basic structure)
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('lawyer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lawyers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('last_message', sa.Text(), nullable=True),
        sa.Column('last_message_date', sa.DateTime(), nullable=True),
        sa.Column('unread_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    
    op.create_table(
        'conversation_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('user_id_from', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id_to', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('from_lawyer', sa.Boolean(), default=False),
        sa.Column('read', sa.Boolean(), default=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )