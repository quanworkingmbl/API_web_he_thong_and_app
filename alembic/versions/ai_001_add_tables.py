"""add AI tables - moderation logs, generation cache, cost logs, product embeddings

Revision ID: ai_001_add_tables
Revises: 
Create Date: 2026-04-08
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = 'ai_001_add_tables'
down_revision = None
branch_labels = ('ai',)
depends_on = None


def upgrade() -> None:
    # --- ai_moderation_logs ---
    op.create_table(
        'ai_moderation_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('content_id', sa.Integer(), nullable=True),
        sa.Column('rule_engine_result', sa.String(20), nullable=True),
        sa.Column('rule_engine_flags', sa.Text(), nullable=True),
        sa.Column('model_used', sa.String(100), nullable=False),
        sa.Column('ai_decision', sa.String(20), nullable=False),
        sa.Column('ai_confidence', sa.Float(), nullable=True),
        sa.Column('ai_reasons', sa.Text(), nullable=True),
        sa.Column('ai_flags', sa.Text(), nullable=True),
        sa.Column('escalated', sa.Boolean(), default=False),
        sa.Column('escalation_reason', sa.String(200), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('input_tokens', sa.Integer(), default=0),
        sa.Column('output_tokens', sa.Integer(), default=0),
        sa.Column('estimated_cost_usd', sa.Float(), default=0.0),
        sa.Column('raw_response', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.ForeignKeyConstraint(['content_id'], ['contents.id']),
    )
    op.create_index('ix_ai_moderation_logs_id', 'ai_moderation_logs', ['id'])
    op.create_index('ix_ai_moderation_logs_product_id', 'ai_moderation_logs', ['product_id'])
    op.create_index('ix_ai_moderation_logs_content_id', 'ai_moderation_logs', ['content_id'])

    # --- ai_generation_cache ---
    op.create_table(
        'ai_generation_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('input_hash', sa.String(64), nullable=False),
        sa.Column('task_type', sa.String(30), nullable=False),
        sa.Column('model_used', sa.String(100), nullable=True),
        sa.Column('input_text', sa.Text(), nullable=True),
        sa.Column('output_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('input_hash'),
    )
    op.create_index('ix_ai_generation_cache_id', 'ai_generation_cache', ['id'])
    op.create_index('ix_ai_generation_cache_input_hash', 'ai_generation_cache', ['input_hash'])
    op.create_index('ix_ai_generation_cache_expires_at', 'ai_generation_cache', ['expires_at'])

    # --- ai_cost_logs ---
    op.create_table(
        'ai_cost_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('log_date', sa.Date(), nullable=False),
        sa.Column('model_id', sa.String(100), nullable=False),
        sa.Column('task_type', sa.String(30), nullable=False),
        sa.Column('request_count', sa.Integer(), default=0),
        sa.Column('total_input_tokens', sa.Integer(), default=0),
        sa.Column('total_output_tokens', sa.Integer(), default=0),
        sa.Column('total_cost_usd', sa.Float(), default=0.0),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('log_date', 'model_id', 'task_type', name='uq_cost_date_model_task'),
    )
    op.create_index('ix_ai_cost_logs_id', 'ai_cost_logs', ['id'])
    op.create_index('ix_ai_cost_logs_log_date', 'ai_cost_logs', ['log_date'])

    # --- product_embeddings ---
    op.create_table(
        'product_embeddings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('embedding_text', sa.Text(), nullable=True),
        sa.Column('embedding_vector', sa.Text(), nullable=True),
        sa.Column('vector_dimension', sa.Integer(), nullable=True),
        sa.Column('model_version', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.UniqueConstraint('product_id'),
    )
    op.create_index('ix_product_embeddings_id', 'product_embeddings', ['id'])
    op.create_index('ix_product_embeddings_product_id', 'product_embeddings', ['product_id'])


def downgrade() -> None:
    op.drop_table('product_embeddings')
    op.drop_table('ai_cost_logs')
    op.drop_table('ai_generation_cache')
    op.drop_table('ai_moderation_logs')
