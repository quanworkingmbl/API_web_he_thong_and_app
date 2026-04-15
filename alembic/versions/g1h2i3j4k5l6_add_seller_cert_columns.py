"""Add seller profile cert columns and remove INDIVIDUAL from API

Revision ID: g1h2i3j4k5l6
Revises: e7f8a9b0c1d2
Create Date: 2026-04-16

Changes:
- seller_profiles: thêm business_registration_cert_url (Giấy CN ĐKKD)
- seller_profiles: thêm food_safety_cert_url (Giấy CN ATTP)
- Ghi chú: INDIVIDUAL không còn cho phép qua API nhưng vẫn giữ trong DB enum
  để backward-compatible với các records cũ.
"""
from alembic import op
import sqlalchemy as sa

revision = "g1h2i3j4k5l6"
down_revision = "1d50cbd85214"
branch_labels = None
depends_on = None



def upgrade() -> None:
    # Thêm cột business_registration_cert_url
    op.add_column(
        "seller_profiles",
        sa.Column("business_registration_cert_url", sa.Text(), nullable=True,
                  comment="Giấy CN Đăng ký Kinh doanh – bản sao công chứng")
    )
    # Thêm cột food_safety_cert_url
    op.add_column(
        "seller_profiles",
        sa.Column("food_safety_cert_url", sa.Text(), nullable=True,
                  comment="Giấy CN Cơ sở đủ điều kiện An toàn thực phẩm")
    )


def downgrade() -> None:
    op.drop_column("seller_profiles", "food_safety_cert_url")
    op.drop_column("seller_profiles", "business_registration_cert_url")
