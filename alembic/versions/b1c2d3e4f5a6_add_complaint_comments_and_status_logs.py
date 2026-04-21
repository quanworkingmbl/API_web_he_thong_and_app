"""add_complaint_comments_and_status_logs

Revision ID: b1c2d3e4f5a6
Revises: a0b1c2d3e4f5
Create Date: 2026-04-05 11:13:00.000000

Thay đổi:
1. Thêm cột vào bảng `complaints`:
   - category     (enum ComplaintCategory)
   - priority     (enum ComplaintPriority)
   - images       (Text, nullable)
   - resolution_type (String30, nullable)
   - return_request_id (FK return_requests.id, nullable)
   - assigned_at, first_response_at, resolved_at, closed_at (DateTime nullable)

2. Tạo bảng `complaint_comments` (thread trao đổi)

3. Tạo bảng `complaint_status_logs` (audit trail)
"""
from alembic import op
import sqlalchemy as sa


revision = 'b1c2d3e4f5a6'
down_revision = 'a0b1c2d3e4f5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Tạo Enum types (PostgreSQL) ──────────────────────────────────────────
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE complaintcategory AS ENUM
                ('DELIVERY','QUALITY','REFUND','FRAUD','SERVICE','OTHER');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE complaintpriority AS ENUM
                ('LOW','MEDIUM','HIGH','URGENT');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE commentrole AS ENUM
                ('buyer','seller','admin','system');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)

    # 1. Thêm cột vào complaints
    op.add_column('complaints', sa.Column(
        'category',
        sa.Enum('DELIVERY','QUALITY','REFUND','FRAUD','SERVICE','OTHER', name='complaintcategory'),
        nullable=False, server_default='OTHER'
    ))
    op.add_column('complaints', sa.Column(
        'priority',
        sa.Enum('LOW','MEDIUM','HIGH','URGENT', name='complaintpriority'),
        nullable=False, server_default='MEDIUM'
    ))
    op.add_column('complaints', sa.Column('images',          sa.Text(),       nullable=True))
    op.add_column('complaints', sa.Column('resolution_type', sa.String(30),   nullable=True))
    op.add_column('complaints', sa.Column('return_request_id', sa.Integer(),  nullable=True))
    op.add_column('complaints', sa.Column('assigned_at',       sa.DateTime(timezone=True), nullable=True))
    op.add_column('complaints', sa.Column('first_response_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('complaints', sa.Column('resolved_at',       sa.DateTime(timezone=True), nullable=True))
    op.add_column('complaints', sa.Column('closed_at',         sa.DateTime(timezone=True), nullable=True))

    op.create_index('ix_complaints_category', 'complaints', ['category'])
    op.create_index('ix_complaints_priority', 'complaints', ['priority'])

    # FK return_request_id
    op.create_foreign_key(
        'fk_complaints_return_request_id',
        'complaints', 'return_requests',
        ['return_request_id'], ['id'],
        ondelete='SET NULL'
    )

    # 2. Tạo bảng complaint_comments
    op.create_table(
        'complaint_comments',
        sa.Column('id',           sa.Integer(), nullable=False),
        sa.Column('complaint_id', sa.Integer(), nullable=False),
        sa.Column('author_id',    sa.Integer(), nullable=False),
        sa.Column('role', sa.Enum('buyer','seller','admin','system', name='commentrole'), nullable=False),
        sa.Column('message',      sa.Text(),    nullable=False),
        sa.Column('attachments',  sa.Text(),    nullable=True),
        sa.Column('is_internal',  sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at',   sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['author_id'],    ['users.id'],      ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_complaint_comments_id',           'complaint_comments', ['id'])
    op.create_index('ix_complaint_comments_complaint_id', 'complaint_comments', ['complaint_id'])

    # 3. Tạo bảng complaint_status_logs
    op.create_table(
        'complaint_status_logs',
        sa.Column('id',           sa.Integer(),    nullable=False),
        sa.Column('complaint_id', sa.Integer(),    nullable=False),
        sa.Column('old_status',   sa.String(30),   nullable=True),
        sa.Column('new_status',   sa.String(30),   nullable=False),
        sa.Column('actor_id',     sa.Integer(),    nullable=True),
        sa.Column('note',         sa.Text(),       nullable=True),
        sa.Column('timestamp',    sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'],  ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['actor_id'],     ['users.id'],       ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_complaint_status_logs_id',           'complaint_status_logs', ['id'])
    op.create_index('ix_complaint_status_logs_complaint_id', 'complaint_status_logs', ['complaint_id'])


def downgrade() -> None:
    # 3. Drop complaint_status_logs
    op.drop_index('ix_complaint_status_logs_complaint_id', table_name='complaint_status_logs')
    op.drop_index('ix_complaint_status_logs_id',           table_name='complaint_status_logs')
    op.drop_table('complaint_status_logs')

    # 2. Drop complaint_comments
    op.drop_index('ix_complaint_comments_complaint_id', table_name='complaint_comments')
    op.drop_index('ix_complaint_comments_id',           table_name='complaint_comments')
    op.drop_table('complaint_comments')

    # 1. Drop cột thêm vào complaints
    op.drop_constraint('fk_complaints_return_request_id', 'complaints', type_='foreignkey')
    op.drop_index('ix_complaints_priority', table_name='complaints')
    op.drop_index('ix_complaints_category', table_name='complaints')

    for col in ['closed_at','resolved_at','first_response_at','assigned_at',
                'return_request_id','resolution_type','images','priority','category']:
        op.drop_column('complaints', col)

    op.execute('DROP TYPE IF EXISTS commentrole')
    op.execute('DROP TYPE IF EXISTS complaintpriority')
    op.execute('DROP TYPE IF EXISTS complaintcategory')
