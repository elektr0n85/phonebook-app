"""Add password reset token fields to users

Revision ID: add_reset_token_fields
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_reset_token_fields'
down_revision = None  # Update this to point to previous migration if exists
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add reset_token and reset_token_expires columns to users table."""
    op.add_column('users', sa.Column('reset_token', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('reset_token_expires', sa.DateTime(), nullable=True))
    
    # Add index for faster token lookups
    op.create_index('ix_users_reset_token', 'users', ['reset_token'])


def downgrade() -> None:
    """Remove reset_token and reset_token_expires columns from users table."""
    op.drop_index('ix_users_reset_token', table_name='users')
    op.drop_column('users', 'reset_token_expires')
    op.drop_column('users', 'reset_token')
