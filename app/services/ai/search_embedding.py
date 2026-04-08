"""
AI Search Embedding Service
- Tạo embedding cho sản phẩm dùng Titan v2
- Vector search (cosine similarity) + Lexical hybrid
- Normalize text tiếng Việt
"""

import json
import math
import re
import unicodedata
import logging
import time
from typing import List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.ai.bedrock_client import bedrock_client, BedrockClientError
from app.services.ai.cost_tracker import log_ai_cost
from app.services.ai.cache import generate_cache_key, get_cached_response, set_cached_response

logger = logging.getLogger(__name__)


# ==============================================================================
# TEXT NORMALIZATION (Vietnamese)
# ==============================================================================

def normalize_text(input_text: str) -> str:
    """
    Chuẩn hóa text cho embedding.
    - Unicode NFC
    - Lowercase
    - Remove extra whitespace
    - Remove special characters (giữ tiếng Việt)
    """
    if not input_text:
        return ""

    text = unicodedata.normalize("NFC", input_text)
    text = text.lower().strip()

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)

    # Remove URLs
    text = re.sub(r'https?://\S+', ' ', text)

    # Remove excessive punctuation nhưng giữ dấu tiếng Việt
    text = re.sub(r'[^\w\s\u00C0-\u024F\u1E00-\u1EFF]', ' ', text)

    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


# ==============================================================================
# SEARCH EMBEDDING SERVICE
# ==============================================================================

class SearchEmbeddingService:
    """Tìm kiếm ngữ nghĩa sản phẩm bằng Titan Embedding v2."""

    @classmethod
    async def create_embedding(cls, text: str, db: Optional[Session] = None) -> List[float]:
        """Tạo embedding vector cho một đoạn text."""
        normalized = normalize_text(text)
        if not normalized:
            return []

        # Limit input (Titan v2 max 8K tokens)
        normalized = normalized[:3000]

        try:
            response = await bedrock_client.invoke_titan_embedding(
                text=normalized,
                timeout=settings.AI_EMBEDDING_TIMEOUT,
            )

            embedding = response.get("embedding", [])

            # Log cost
            if db:
                log_ai_cost(
                    db, settings.BEDROCK_EMBEDDING_MODEL_ID, "embedding",
                    response.get("input_tokens", 0), 0,
                    response.get("estimated_cost_usd", 0.0),
                )

            return embedding

        except BedrockClientError as e:
            logger.error("Embedding creation failed: %s", e)
            raise

    @classmethod
    async def index_product(cls, db: Session, product_id: int) -> bool:
        """
        Tạo/cập nhật embedding cho một sản phẩm.
        Kết hợp name + description + category + region để tạo document text.
        """
        from app.models.product import Product
        from app.models.category import Category
        from app.models.ai_log import ProductEmbedding

        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            logger.warning("Product not found for indexing: id=%d", product_id)
            return False

        # Build document text
        parts = [product.name or ""]
        if product.description:
            parts.append(product.description)
        if product.category_id:
            category = db.query(Category).filter(Category.id == product.category_id).first()
            if category:
                parts.append(category.name)
        if product.label:
            parts.append(product.label)

        doc_text = " ".join(parts)
        normalized = normalize_text(doc_text)

        if not normalized:
            return False

        # Create embedding
        try:
            embedding = await cls.create_embedding(normalized, db)
            if not embedding:
                return False
        except BedrockClientError:
            return False

        # Save to DB (upsert)
        existing = db.query(ProductEmbedding).filter(
            ProductEmbedding.product_id == product_id
        ).first()

        embedding_json = json.dumps(embedding)

        if existing:
            existing.embedding_text = normalized[:5000]
            existing.embedding_vector = embedding_json
            existing.vector_dimension = len(embedding)
            existing.model_version = settings.BEDROCK_EMBEDDING_MODEL_ID
        else:
            entry = ProductEmbedding(
                product_id=product_id,
                embedding_text=normalized[:5000],
                embedding_vector=embedding_json,
                vector_dimension=len(embedding),
                model_version=settings.BEDROCK_EMBEDDING_MODEL_ID,
            )
            db.add(entry)

        try:
            db.commit()
            logger.info("Product indexed: id=%d dim=%d", product_id, len(embedding))
            return True
        except Exception as e:
            db.rollback()
            logger.error("Failed to save embedding: %s", e)
            return False

    @classmethod
    async def search(
        cls,
        db: Session,
        query: str,
        top_k: int = 10,
    ) -> List[dict]:
        """
        Hybrid search: vector similarity + lexical fallback.
        Returns list of {product_id, score, name, ...}
        """
        from app.models.product import Product, ProductStatus
        from app.models.ai_log import ProductEmbedding

        normalized_query = normalize_text(query)
        if not normalized_query:
            return []

        results = []

        # --- Vector Search ---
        try:
            query_embedding = await cls.create_embedding(normalized_query, db)
            if query_embedding:
                # Load ALL embeddings (for small-medium catalogs)
                # For large catalogs, pgvector or external vector DB would be better
                all_embeddings = db.query(ProductEmbedding).all()

                scored = []
                for emb in all_embeddings:
                    try:
                        stored_vector = json.loads(emb.embedding_vector)
                        similarity = cls._cosine_similarity(query_embedding, stored_vector)
                        if similarity > 0.3:  # Threshold
                            scored.append((emb.product_id, similarity))
                    except (json.JSONDecodeError, ValueError):
                        continue

                scored.sort(key=lambda x: x[1], reverse=True)
                vector_hits = scored[:top_k]

                for pid, score in vector_hits:
                    results.append({
                        "product_id": pid,
                        "score": round(score, 4),
                        "source": "vector",
                    })

        except BedrockClientError:
            logger.warning("Vector search failed, falling back to lexical only")

        # --- Lexical Search (fallback/supplement) ---
        lexical_products = (
            db.query(Product)
            .filter(
                Product.status == ProductStatus.APPROVED,
                Product.is_active == True,
                Product.name.ilike(f"%{query}%"),
            )
            .limit(top_k)
            .all()
        )

        existing_ids = {r["product_id"] for r in results}
        for p in lexical_products:
            if p.id not in existing_ids:
                results.append({
                    "product_id": p.id,
                    "score": 0.5,  # Default score for lexical matches
                    "source": "lexical",
                })

        # --- Enrich with product data ---
        enriched = []
        for r in results[:top_k]:
            product = db.query(Product).filter(Product.id == r["product_id"]).first()
            if product and product.status == ProductStatus.APPROVED and product.is_active:
                enriched.append({
                    "product_id": product.id,
                    "name": product.name,
                    "description": (product.description or "")[:200],
                    "price": float(product.price) if product.price else 0,
                    "label": product.label,
                    "images": product.images,
                    "score": r["score"],
                    "source": r["source"],
                })

        # Sort by score
        enriched.sort(key=lambda x: x["score"], reverse=True)
        return enriched

    @classmethod
    async def rebuild_index(cls, db: Session) -> dict:
        """Rebuild toàn bộ embedding index. Trả về stats."""
        from app.models.product import Product, ProductStatus

        products = (
            db.query(Product)
            .filter(
                Product.status == ProductStatus.APPROVED,
                Product.is_active == True,
            )
            .all()
        )

        success = 0
        failed = 0

        for product in products:
            try:
                ok = await cls.index_product(db, product.id)
                if ok:
                    success += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error("Index rebuild failed for product %d: %s", product.id, e)
                failed += 1

        return {
            "total_products": len(products),
            "indexed": success,
            "failed": failed,
        }

    # --------------------------------------------------------------------------
    # MATH HELPERS
    # --------------------------------------------------------------------------

    @staticmethod
    def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """Tính cosine similarity giữa 2 vectors."""
        if len(vec_a) != len(vec_b) or not vec_a:
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)
