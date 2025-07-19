"""add user_id_from and user_id_to to conversation_messages

Revision ID: 4f400c93279a
Revises: 399e987821c8
Create Date: 2025-07-19 14:08:18.202980

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4f400c93279a'
down_revision = '399e987821c8'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Delete all existing conversation messages to start fresh
    op.execute("DELETE FROM conversation_messages")

    # Delete all existing conversation to start fresh
    op.execute("DELETE FROM conversations")
    
    # Reset conversation metadata since we're clearing all messages
    op.execute("UPDATE conversations SET last_message = NULL, unread_count = 0")
    
    # Add user_id_from column
    op.add_column('conversation_messages', sa.Column('user_id_from', postgresql.UUID(as_uuid=True), nullable=False))
    
    # Add user_id_to column
    op.add_column('conversation_messages', sa.Column('user_id_to', postgresql.UUID(as_uuid=True), nullable=False))
    
    # Add foreign key constraints
    op.create_foreign_key(
        'fk_conversation_messages_user_id_from', 
        'conversation_messages', 
        'users', 
        ['user_id_from'], 
        ['id'], 
        ondelete='CASCADE'
    )
    
    op.create_foreign_key(
        'fk_conversation_messages_user_id_to', 
        'conversation_messages', 
        'users', 
        ['user_id_to'], 
        ['id'], 
        ondelete='CASCADE'
    )
    
    # Add indexes for performance
    op.create_index('ix_conversation_messages_user_id_from', 'conversation_messages', ['user_id_from'])
    op.create_index('ix_conversation_messages_user_id_to', 'conversation_messages', ['user_id_to'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_conversation_messages_user_id_to', table_name='conversation_messages')
    op.drop_index('ix_conversation_messages_user_id_from', table_name='conversation_messages')
    
    # Drop foreign key constraints
    op.drop_constraint('fk_conversation_messages_user_id_to', 'conversation_messages', type_='foreignkey')
    op.drop_constraint('fk_conversation_messages_user_id_from', 'conversation_messages', type_='foreignkey')
    
    # Drop columns
    op.drop_column('conversation_messages', 'user_id_to')
    op.drop_column('conversation_messages', 'user_id_from')