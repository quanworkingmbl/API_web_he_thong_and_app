"""merge ai and auth refresh branches

Revision ID: 1d50cbd85214
Revises: ai_001_add_tables, f4a5b6c7d8e9
Create Date: 2026-04-09 00:00:12.915529

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d50cbd85214'
down_revision = ('ai_001_add_tables', 'f4a5b6c7d8e9')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

