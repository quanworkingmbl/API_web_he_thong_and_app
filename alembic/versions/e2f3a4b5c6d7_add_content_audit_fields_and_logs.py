"""add_content_audit_fields_and_logs

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-04-05 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e2f3a4b5c6d7'
down_revision = 'd1e2f3a4b5c6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add soft delete and audit fields to contents table
    op.add_column('contents', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'))
    op.add_column('contents', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('contents', sa.Column('deleted_by', sa.Integer(), nullable=True))
    op.add_column('contents', sa.Column('rejection_reason', sa.Text(), nullable=True))
    
    # Add foreign key for deleted_by
    op.create_foreign_key('fk_contents_deleted_by', 'contents', 'users', ['deleted_by'], ['id'])
    
    # Create index on is_active
    op.create_index('ix_contents_is_active', 'contents', ['is_active'])
    
    # Create content_audit_logs table
    op.create_table(
        'content_audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.Enum('CREATE', 'UPDATE', 'APPROVE', 'REJECT', 'DELETE', 'RESTORE', name='contentauditaction'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('old_status', sa.String(20), nullable=True),
        sa.Column('new_status', sa.String(20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['content_id'], ['contents.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_content_audit_logs_id', 'content_audit_logs', ['id'])
    op.create_index('ix_content_audit_logs_content_id', 'content_audit_logs', ['content_id'])


def downgrade() -> None:
    # Drop content_audit_logs table
    op.drop_index('ix_content_audit_logs_content_id', table_name='content_audit_logs')
    op.drop_index('ix_content_audit_logs_id', table_name='content_audit_logs')
    op.drop_table('content_audit_logs')
    
    # Drop enum type
    op.execute('DROP TYPE IF EXISTS contentauditaction')
    
    # Drop added columns from contents
    op.drop_index('ix_contents_is_active', table_name='contents')
    op.drop_constraint('fk_contents_deleted_by', 'contents', type_='foreignkey')
    op.drop_column('contents', 'rejection_reason')
    op.drop_column('contents', 'deleted_by')
    op.drop_column('contents', 'deleted_at')
    op.drop_column('contents', 'is_active')
