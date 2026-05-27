"""
AI API Endpoints
Cung cấp REST API cho tất cả AI features:
- Moderation (product + content)
- Content generation (description, blog, SEO meta)
- Search embedding (index, search, rebuild)
- Monitoring (stats, cost report, moderation logs)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date, datetime, timedelta
from pydantic import BaseModel, Field, ConfigDict

from app.core.database import get_db
from app.core.config import settings
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.ai.vertex_client import VertexAIClientError

router = APIRouter()


def _is_vertex_permission_denied(error: Exception) -> bool:
    message = str(error)
    return (
        "PermissionDenied" in message
        or "permission denied" in message.lower()
        or getattr(error, "status_code", None) == 403
    )


# ==============================================================================
# REQUEST/RESPONSE SCHEMAS
# ==============================================================================


class AIBaseSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())


class ModerationResponse(AIBaseSchema):
    success: bool
    decision: str
    confidence: float
    reasons: list
    flags: list
    source: str
    model_used: str
    escalated: bool
    processing_time_ms: int
    estimated_cost_usd: float


class GenerateDescriptionRequest(AIBaseSchema):
    name: str = Field(default="", description="Tên sản phẩm (nếu không dùng product_id)")
    category: str = ""
    region: str = ""
    ingredients: str = ""
    process: str = ""
    certificates: str = ""
    highlights: str = ""
    use_sonnet: bool = Field(False, description="Bật model sáng tạo (chất lượng cao hơn, chi phí cao hơn)")


class GenerateBlogRequest(AIBaseSchema):
    topic: str = Field(..., min_length=5, max_length=300)
    main_keyword: str = ""
    secondary_keywords: str = ""
    word_count: int = Field(800, ge=300, le=3000)
    related_products: str = ""
    notes: str = ""
    use_sonnet: bool = False


class GenerateDescriptionResponse(AIBaseSchema):
    success: bool
    description: str
    model_used: str
    cached: bool
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    latency_ms: int


class GenerateBlogResponse(AIBaseSchema):
    success: bool
    content: str
    model_used: str
    cached: bool
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    latency_ms: int


class SearchResponse(AIBaseSchema):
    success: bool
    results: list
    query: str
    total: int


# ==============================================================================
# MODERATION ENDPOINTS
# ==============================================================================

@router.post("/moderate/product/{product_id}", response_model=ModerationResponse)
async def moderate_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Kiểm duyệt sản phẩm bằng AI.
    Pipeline: Rule Engine -> Gemini Flash -> (creative model escalation nếu cần)
    Quyền: admin, content_manager
    """
    if current_user.type not in ("admin", "content_manager"):
        raise HTTPException(status_code=403, detail="Chỉ admin/content_manager mới có thể sử dụng AI moderation")

    from app.models.product import Product
    from app.models.category import Category

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")

    category = db.query(Category).filter(Category.id == product.category_id).first() if product.category_id else None

    # Xác định sản phẩm có ưu tiên cao không
    is_high_value = product.label in ("OCOP", "CLEAN_AGRICULTURE")

    from app.services.ai.moderation import ModerationService

    try:
        result = await ModerationService.moderate_product(
            db=db,
            product_id=product_id,
            name=product.name,
            description=product.description or "",
            category=category.name if category else "",
            category_id=product.category_id,
            price=float(product.price) if product.price else 0,
            label=product.label or "",
            is_high_value=is_high_value,
        )
    except VertexAIClientError as e:
        if _is_vertex_permission_denied(e):
            raise HTTPException(
                status_code=503,
                detail="AI service chưa được cấp quyền Vertex AI cho model hiện tại. Vui lòng liên hệ admin hệ thống.",
            )
        raise HTTPException(status_code=502, detail=f"AI moderation service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI moderation error: {str(e)}")

    return ModerationResponse(
        success=True,
        decision=result.decision,
        confidence=result.confidence,
        reasons=result.reasons,
        flags=result.flags,
        source=result.source,
        model_used=result.model_used,
        escalated=result.escalated,
        processing_time_ms=result.processing_time_ms,
        estimated_cost_usd=result.estimated_cost_usd,
    )


@router.post("/moderate/content/{content_id}", response_model=ModerationResponse)
async def moderate_content(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Kiểm duyệt content/blog bằng AI.
    Quyền: admin, content_manager
    """
    if current_user.type not in ("admin", "content_manager"):
        raise HTTPException(status_code=403, detail="Chỉ admin/content_manager mới có thể sử dụng AI moderation")

    from app.models.content import Content

    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content không tồn tại")

    from app.services.ai.moderation import ModerationService

    try:
        result = await ModerationService.moderate_content(
            db=db,
            content_id=content_id,
            title=content.title,
            content_text=content.content or "",
            content_type=content.content_type or "",
        )
    except VertexAIClientError as e:
        if _is_vertex_permission_denied(e):
            raise HTTPException(
                status_code=503,
                detail="AI service chưa được cấp quyền Vertex AI cho model hiện tại. Vui lòng liên hệ admin hệ thống.",
            )
        raise HTTPException(status_code=502, detail=f"AI moderation service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI moderation error: {str(e)}")

    return ModerationResponse(
        success=True,
        decision=result.decision,
        confidence=result.confidence,
        reasons=result.reasons,
        flags=result.flags,
        source=result.source,
        model_used=result.model_used,
        escalated=result.escalated,
        processing_time_ms=result.processing_time_ms,
        estimated_cost_usd=result.estimated_cost_usd,
    )


# ==============================================================================
# CONTENT GENERATION ENDPOINTS
# ==============================================================================

@router.post("/generate/description/{product_id}", response_model=GenerateDescriptionResponse)
async def generate_product_description(
    product_id: int,
    request_data: GenerateDescriptionRequest = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Sinh mô tả sản phẩm bằng AI.
    Tự động lấy thông tin từ product trong DB, có thể bổ sung qua request body.
    """
    if current_user.type not in ("admin", "content_manager", "producer", "seller"):
        raise HTTPException(status_code=403, detail="Không có quyền sử dụng tính năng này")

    from app.models.product import Product
    from app.models.category import Category
    from app.models.traceability import ProductCertificate, ProductOrigin

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")

    # Ownership check cho seller
    is_admin = current_user.type in ("admin", "content_manager")
    if not is_admin and product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bạn chỉ có thể sinh mô tả cho sản phẩm của mình")

    # Lấy thông tin bổ sung
    category = db.query(Category).filter(Category.id == product.category_id).first() if product.category_id else None

    # Certificates
    certs = db.query(ProductCertificate).filter(ProductCertificate.product_id == product_id).all()
    cert_text = ", ".join(c.certificate_name for c in certs) if certs else ""

    # Origin
    origin = db.query(ProductOrigin).filter(ProductOrigin.product_id == product_id).first()

    req = request_data or GenerateDescriptionRequest()

    from app.services.ai.content_generator import ContentGenerator

    try:
        result = await ContentGenerator.generate_product_description(
            db=db,
            name=req.name or product.name,
            category=req.category or (category.name if category else ""),
            region=req.region or (origin.village_name if origin else ""),
            ingredients=req.ingredients or (origin.ingredients if origin else ""),
            process=req.process or (origin.process_summary if origin else ""),
            certificates=req.certificates or cert_text,
            highlights=req.highlights or "",
            use_sonnet=req.use_sonnet,
        )
    except VertexAIClientError as e:
        if _is_vertex_permission_denied(e):
            raise HTTPException(
                status_code=503,
                detail="AI service chưa được cấp quyền Vertex AI cho model hiện tại. Vui lòng liên hệ admin hệ thống.",
            )
        raise HTTPException(status_code=502, detail=f"AI generation service error: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation error: {str(e)}")

    return GenerateDescriptionResponse(
        success=True,
        description=result["description"],
        model_used=result["model_used"],
        cached=result["cached"],
        input_tokens=result["input_tokens"],
        output_tokens=result["output_tokens"],
        estimated_cost_usd=result["estimated_cost_usd"],
        latency_ms=result["latency_ms"],
    )


@router.post("/generate/description", response_model=GenerateDescriptionResponse)
async def generate_description_freeform(
    request_data: GenerateDescriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Sinh mô tả sản phẩm từ thông tin nhập tự do (không cần product_id).
    """
    if current_user.type not in ("admin", "content_manager", "producer", "seller"):
        raise HTTPException(status_code=403, detail="Không có quyền sử dụng tính năng này")

    if not request_data.name:
        raise HTTPException(status_code=400, detail="Tên sản phẩm là bắt buộc")

    from app.services.ai.content_generator import ContentGenerator

    try:
        result = await ContentGenerator.generate_product_description(
            db=db,
            name=request_data.name,
            category=request_data.category,
            region=request_data.region,
            ingredients=request_data.ingredients,
            process=request_data.process,
            certificates=request_data.certificates,
            highlights=request_data.highlights,
            use_sonnet=request_data.use_sonnet,
        )
    except VertexAIClientError as e:
        if _is_vertex_permission_denied(e):
            raise HTTPException(
                status_code=503,
                detail="AI service chưa được cấp quyền Vertex AI cho model hiện tại. Vui lòng liên hệ admin hệ thống.",
            )
        raise HTTPException(status_code=502, detail=f"AI generation service error: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation error: {str(e)}")

    return GenerateDescriptionResponse(
        success=True,
        description=result["description"],
        model_used=result["model_used"],
        cached=result["cached"],
        input_tokens=result["input_tokens"],
        output_tokens=result["output_tokens"],
        estimated_cost_usd=result["estimated_cost_usd"],
        latency_ms=result["latency_ms"],
    )


@router.post("/generate/blog", response_model=GenerateBlogResponse)
async def generate_blog(
    request_data: GenerateBlogRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Sinh bài blog SEO bằng AI."""
    if current_user.type not in ("admin", "content_manager"):
        raise HTTPException(status_code=403, detail="Chỉ admin/content_manager mới có thể sinh blog AI")

    from app.services.ai.content_generator import ContentGenerator

    try:
        result = await ContentGenerator.generate_blog(
            db=db,
            topic=request_data.topic,
            main_keyword=request_data.main_keyword,
            secondary_keywords=request_data.secondary_keywords,
            word_count=request_data.word_count,
            related_products=request_data.related_products,
            notes=request_data.notes,
            use_sonnet=request_data.use_sonnet,
        )
    except VertexAIClientError as e:
        if _is_vertex_permission_denied(e):
            raise HTTPException(
                status_code=503,
                detail="AI service chưa được cấp quyền Vertex AI cho model hiện tại. Vui lòng liên hệ admin hệ thống.",
            )
        raise HTTPException(status_code=502, detail=f"AI blog generation service error: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI blog generation error: {str(e)}")

    return GenerateBlogResponse(
        success=True,
        content=result["content"],
        model_used=result["model_used"],
        cached=result["cached"],
        input_tokens=result["input_tokens"],
        output_tokens=result["output_tokens"],
        estimated_cost_usd=result["estimated_cost_usd"],
        latency_ms=result["latency_ms"],
    )


@router.post("/generate/seo-meta/{product_id}")
async def generate_seo_meta(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Sinh SEO metadata (title, description, keywords) cho sản phẩm."""
    if current_user.type not in ("admin", "content_manager", "producer", "seller"):
        raise HTTPException(status_code=403, detail="Không có quyền sử dụng tính năng này")

    from app.models.product import Product
    from app.models.category import Category

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")

    category = db.query(Category).filter(Category.id == product.category_id).first() if product.category_id else None

    from app.services.ai.content_generator import ContentGenerator

    try:
        result = await ContentGenerator.generate_seo_meta(
            db=db,
            name=product.name,
            category=category.name if category else "",
            description_short=(product.description or "")[:300],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SEO meta generation error: {str(e)}")

    return {"success": True, **result}


# ==============================================================================
# SEARCH ENDPOINTS (Backend only — không tích hợp UI)
# ==============================================================================

@router.get("/search", response_model=SearchResponse)
async def ai_search(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    top_k: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Tìm kiếm sản phẩm bằng AI embedding (hybrid: vector + lexical)."""
    from app.services.ai.search_embedding import SearchEmbeddingService

    try:
        results = await SearchEmbeddingService.search(db=db, query=q, top_k=top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

    return SearchResponse(
        success=True,
        results=results,
        query=q,
        total=len(results),
    )


@router.post("/index/product/{product_id}")
async def index_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Tạo embedding index cho một sản phẩm."""
    if current_user.type not in ("admin", "content_manager"):
        raise HTTPException(status_code=403, detail="Chỉ admin mới có thể index sản phẩm")

    from app.services.ai.search_embedding import SearchEmbeddingService

    try:
        ok = await SearchEmbeddingService.index_product(db=db, product_id=product_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Index error: {str(e)}")

    if not ok:
        raise HTTPException(status_code=400, detail="Không thể index sản phẩm (thiếu dữ liệu hoặc lỗi)")

    return {"success": True, "message": f"Product {product_id} indexed successfully"}


@router.post("/index/rebuild")
async def rebuild_index(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Rebuild toàn bộ embedding index. CHÚ Ý: tốn thời gian và chi phí."""
    if current_user.type != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới có thể rebuild index")

    from app.services.ai.search_embedding import SearchEmbeddingService

    try:
        stats = await SearchEmbeddingService.rebuild_index(db=db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rebuild error: {str(e)}")

    return {"success": True, "message": "Index rebuild completed", **stats}


# ==============================================================================
# MONITORING ENDPOINTS
# ==============================================================================

@router.get("/stats")
async def get_ai_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Dashboard thống kê AI: moderation, generation, cost."""
    if current_user.type not in ("admin", "content_manager"):
        raise HTTPException(status_code=403, detail="Chỉ admin/content_manager mới xem được stats")

    from app.models.ai_log import AIModerationLog, AIGenerationCache, AICostLog

    # Moderation stats (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    total_moderations = db.query(func.count(AIModerationLog.id)).filter(
        AIModerationLog.created_at >= thirty_days_ago
    ).scalar()

    approve_count = db.query(func.count(AIModerationLog.id)).filter(
        AIModerationLog.created_at >= thirty_days_ago,
        AIModerationLog.ai_decision == "APPROVE",
    ).scalar()

    review_count = db.query(func.count(AIModerationLog.id)).filter(
        AIModerationLog.created_at >= thirty_days_ago,
        AIModerationLog.ai_decision == "REVIEW",
    ).scalar()

    reject_count = db.query(func.count(AIModerationLog.id)).filter(
        AIModerationLog.created_at >= thirty_days_ago,
        AIModerationLog.ai_decision == "REJECT",
    ).scalar()

    escalated_count = db.query(func.count(AIModerationLog.id)).filter(
        AIModerationLog.created_at >= thirty_days_ago,
        AIModerationLog.escalated == True,
    ).scalar()

    avg_latency = db.query(func.avg(AIModerationLog.processing_time_ms)).filter(
        AIModerationLog.created_at >= thirty_days_ago,
    ).scalar()

    # Cache stats
    cache_total = db.query(func.count(AIGenerationCache.id)).scalar()
    cache_active = db.query(func.count(AIGenerationCache.id)).filter(
        AIGenerationCache.expires_at > datetime.utcnow()
    ).scalar()

    # Cost today
    from app.services.ai.cost_tracker import get_daily_cost
    today_cost = get_daily_cost(db)

    return {
        "success": True,
        "moderation": {
            "total": total_moderations,
            "approve": approve_count,
            "review": review_count,
            "reject": reject_count,
            "escalated": escalated_count,
            "review_rate": round(review_count / max(total_moderations, 1) * 100, 1),
            "avg_latency_ms": round(float(avg_latency or 0), 0),
        },
        "cache": {
            "total_entries": cache_total,
            "active_entries": cache_active,
        },
        "cost": {
            "today_usd": round(today_cost, 6),
            "daily_budget_usd": settings.AI_DAILY_BUDGET_USD,
            "budget_used_pct": round(today_cost / max(settings.AI_DAILY_BUDGET_USD, 0.01) * 100, 1),
        },
    }


@router.get("/costs")
async def get_cost_report(
    date_from: str = Query(..., description="Start date (YYYY-MM-DD)"),
    date_to: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Báo cáo chi phí AI theo khoảng thời gian."""
    if current_user.type != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới xem được cost report")

    try:
        d_from = date.fromisoformat(date_from)
        d_to = date.fromisoformat(date_to)
    except ValueError:
        raise HTTPException(status_code=400, detail="Date format phải là YYYY-MM-DD")

    if d_from > d_to:
        raise HTTPException(status_code=400, detail="date_from phải <= date_to")

    from app.services.ai.cost_tracker import get_cost_report
    report = get_cost_report(db, d_from, d_to)

    return {"success": True, **report}


@router.get("/moderation-logs")
async def get_moderation_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    decision: Optional[str] = Query(None, pattern="^(APPROVE|REVIEW|REJECT)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Xem lịch sử kiểm duyệt AI."""
    if current_user.type not in ("admin", "content_manager"):
        raise HTTPException(status_code=403, detail="Chỉ admin/content_manager mới xem được logs")

    from app.models.ai_log import AIModerationLog

    query = db.query(AIModerationLog)
    if decision:
        query = query.filter(AIModerationLog.ai_decision == decision)

    total = query.count()
    skip = (page - 1) * limit
    logs = query.order_by(AIModerationLog.created_at.desc()).offset(skip).limit(limit).all()

    import json as json_module

    return {
        "success": True,
        "data": [
            {
                "id": log.id,
                "product_id": log.product_id,
                "content_id": log.content_id,
                "rule_engine_result": log.rule_engine_result,
                "model_used": log.model_used,
                "ai_decision": log.ai_decision,
                "ai_confidence": log.ai_confidence,
                "ai_reasons": json_module.loads(log.ai_reasons) if log.ai_reasons else [],
                "ai_flags": json_module.loads(log.ai_flags) if log.ai_flags else [],
                "escalated": log.escalated,
                "processing_time_ms": log.processing_time_ms,
                "estimated_cost_usd": log.estimated_cost_usd,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
        "meta": {"total": total, "page": page, "limit": limit},
    }
