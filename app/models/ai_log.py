"""
AI Database Models
- AIModerationLog: log kết quả kiểm duyệt AI
- AIGenerationCache: cache kết quả sinh content
- AICostLog: theo dõi chi phí theo ngày
- ProductEmbedding: lưu vector embedding tìm kiếm
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Float, Boolean, Date,
    ForeignKey, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class AIModerationLog(Base):
    """Log kết quả kiểm duyệt AI cho sản phẩm và content."""
    __tablename__ = "ai_moderation_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Liên kết đến product hoặc content (nullable — chỉ 1 trong 2)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=True, index=True)

    # Pipeline info
    rule_engine_result = Column(String(20), nullable=True)      # PASS / REJECT / FLAG
    rule_engine_flags = Column(Text, nullable=True)             # JSON array

    # AI result
    model_used = Column(String(100), nullable=False)            # haiku / sonnet
    ai_decision = Column(String(20), nullable=False)           # APPROVE / REVIEW / REJECT
    ai_confidence = Column(Float, nullable=True)               # 0.0 - 1.0
    ai_reasons = Column(Text, nullable=True)                   # JSON array
    ai_flags = Column(Text, nullable=True)                     # JSON array

    # Escalation
    escalated = Column(Boolean, default=False)                 # Có escalate Sonnet không
    escalation_reason = Column(String(200), nullable=True)

    # Performance
    processing_time_ms = Column(Integer, nullable=True)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    estimated_cost_usd = Column(Float, default=0.0)

    # Raw response (debug)
    raw_response = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", foreign_keys=[product_id])


class AIGenerationCache(Base):
    """Cache AI-generated content (description, blog, SEO meta)."""
    __tablename__ = "ai_generation_cache"

    id = Column(Integer, primary_key=True, index=True)
    input_hash = Column(String(64), unique=True, nullable=False, index=True)

    task_type = Column(String(30), nullable=False)              # description / blog / seo_meta / embedding
    model_used = Column(String(100), nullable=True)
    input_text = Column(Text, nullable=True)                    # Input gốc (truncated)
    output_text = Column(Text, nullable=True)                   # Output đã generate

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)


class AICostLog(Base):
    """Log chi phí AI aggregate theo ngày + model + task."""
    __tablename__ = "ai_cost_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_date = Column(Date, nullable=False, index=True)

    model_id = Column(String(100), nullable=False)
    task_type = Column(String(30), nullable=False)              # moderation / description / blog / embedding

    request_count = Column(Integer, default=0)
    total_input_tokens = Column(Integer, default=0)
    total_output_tokens = Column(Integer, default=0)
    total_cost_usd = Column(Float, default=0.0)

    __table_args__ = (
        UniqueConstraint("log_date", "model_id", "task_type", name="uq_cost_date_model_task"),
    )


class ProductEmbedding(Base):
    """Lưu vector embedding cho sản phẩm — phục vụ tìm kiếm ngữ nghĩa."""
    __tablename__ = "product_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True, nullable=False, index=True)

    embedding_text = Column(Text, nullable=True)                # Text đã normalize trước khi embed
    embedding_vector = Column(Text, nullable=True)              # JSON array of floats
    vector_dimension = Column(Integer, nullable=True)           # Số chiều vector

    model_version = Column(String(100), nullable=True)          # titan-embed-text-v2

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    product = relationship("Product", foreign_keys=[product_id])
