"""
Vertex AI Client Wrapper
- Retry logic with exponential backoff + jitter
- Timeout per operation type
- Cost estimation per request
- Error classification (retryable vs non-retryable)
"""

import asyncio
import logging
import os
import random
import time
from pathlib import Path
from typing import Any, Callable, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    import vertexai
    from google.api_core import exceptions as google_exceptions
    from google.auth.exceptions import GoogleAuthError
    from vertexai.generative_models import GenerationConfig, GenerativeModel
    from vertexai.language_models import TextEmbeddingModel

    VERTEX_IMPORT_ERROR = None
except Exception as import_error:  # pragma: no cover - handled at runtime
    vertexai = None
    google_exceptions = None
    GoogleAuthError = Exception
    GenerationConfig = None
    GenerativeModel = None
    TextEmbeddingModel = None
    VERTEX_IMPORT_ERROR = import_error


# Approximate public pricing (USD per 1K tokens). Update when pricing changes.
MODEL_COSTS = {
    "gemini-1.5-flash": {"input": 0.000075, "output": 0.00030},
    "gemini-1.5-flash-001": {"input": 0.000075, "output": 0.00030},
    "gemini-1.5-flash-002": {"input": 0.000075, "output": 0.00030},
    "gemini-1.5-pro": {"input": 0.00125, "output": 0.00500},
    "gemini-1.5-pro-001": {"input": 0.00125, "output": 0.00500},
    "gemini-1.5-pro-002": {"input": 0.00125, "output": 0.00500},
    "text-embedding-005": {"input": 0.00002, "output": 0.0},
}


class VertexAIClientError(Exception):
    """Base error for Vertex AI operations."""

    def __init__(self, message: str, retryable: bool = False, status_code: int = 500):
        super().__init__(message)
        self.retryable = retryable
        self.status_code = status_code


class VertexAIClient:
    """Singleton-style Vertex AI client with retry, timeout, and cost tracking."""

    _instance: Optional["VertexAIClient"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        self._initialized = True
        self._available = False
        self._init_error = ""
        self._generative_models: dict[str, Any] = {}
        self._embedding_model: Optional[Any] = None
        self._embedding_model_id: str = ""

        try:
            self._initialize_vertex()
            self._available = True
        except Exception as exc:
            self._init_error = str(exc)
            self._available = False
            logger.error("Failed to initialize VertexAIClient: %s", exc)

    @property
    def is_available(self) -> bool:
        return self._available

    def _initialize_vertex(self) -> None:
        if VERTEX_IMPORT_ERROR is not None:
            raise VertexAIClientError(
                f"Missing Vertex AI dependencies: {VERTEX_IMPORT_ERROR}",
                retryable=False,
                status_code=500,
            )

        project_id = (settings.VERTEX_PROJECT_ID or "").strip()
        location = (settings.VERTEX_LOCATION or "us-central1").strip() or "us-central1"

        # The current vertexai SDK does not accept "global" as a location.
        # Keep service available by falling back to a stable default region.
        if location.lower() == "global":
            logger.warning(
                "VERTEX_LOCATION=global is not supported by vertexai SDK; "
                "falling back to us-central1"
            )
            location = "us-central1"

        if not project_id:
            raise VertexAIClientError(
                "VERTEX_PROJECT_ID is required to use Vertex AI",
                retryable=False,
                status_code=503,
            )

        credentials_path = (settings.GOOGLE_APPLICATION_CREDENTIALS or "").strip()
        if credentials_path:
            resolved = Path(credentials_path).expanduser()
            if not resolved.is_absolute():
                resolved = (Path.cwd() / resolved).resolve()

            if not resolved.exists():
                raise VertexAIClientError(
                    f"Service account file not found: {resolved}",
                    retryable=False,
                    status_code=503,
                )

            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(resolved)

        try:
            vertexai.init(project=project_id, location=location)
        except Exception as exc:
            message = str(exc)
            if "Unsupported region" in message:
                configured_location = settings.VERTEX_LOCATION or location
                raise VertexAIClientError(
                    "Unsupported VERTEX_LOCATION='"
                    f"{configured_location}'. Set a supported region such as "
                    "'us-central1'. Original error: "
                    f"{message}",
                    retryable=False,
                    status_code=503,
                ) from exc
            raise
        logger.info(
            "VertexAIClient initialized successfully (project=%s, location=%s)",
            project_id,
            location,
        )

    def _ensure_available(self) -> None:
        if not self.is_available:
            message = "Vertex AI client not initialized"
            if self._init_error:
                message = f"{message}: {self._init_error}"
            raise VertexAIClientError(message, retryable=False, status_code=503)

    def _get_generative_model(self, model_id: str) -> Any:
        if model_id not in self._generative_models:
            self._generative_models[model_id] = GenerativeModel(model_id)
        return self._generative_models[model_id]

    def _get_embedding_model(self, model_id: str) -> Any:
        if self._embedding_model is None or self._embedding_model_id != model_id:
            self._embedding_model = TextEmbeddingModel.from_pretrained(model_id)
            self._embedding_model_id = model_id
        return self._embedding_model

    async def invoke_gemini(
        self,
        prompt: str,
        system_prompt: str = "",
        model_id: Optional[str] = None,
        max_tokens: int = 200,
        temperature: float = 0.0,
        timeout: int = 10,
    ) -> dict:
        """
        Invoke Gemini model via Vertex AI.
        Returns: content, input_tokens, output_tokens, model_id, latency_ms, estimated_cost_usd
        """
        self._ensure_available()

        model = model_id or settings.VERTEX_MODERATION_MODEL_ID
        request_text = prompt.strip()
        if system_prompt:
            request_text = f"SYSTEM INSTRUCTION:\n{system_prompt}\n\nUSER REQUEST:\n{prompt}"

        def _invoke() -> dict:
            model_client = self._get_generative_model(model)
            response = model_client.generate_content(
                request_text,
                generation_config=GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )
            content = self._extract_generated_text(response)
            input_tokens, output_tokens = self._extract_generation_usage(
                response=response,
                request_text=request_text,
                output_text=content,
            )
            return {
                "content": content,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "model_id": model,
            }

        result = await self._run_with_retry(
            operation_name="gemini_generate",
            operation_fn=_invoke,
            timeout=timeout,
        )

        result["estimated_cost_usd"] = self._calculate_cost(
            model,
            result.get("input_tokens", 0),
            result.get("output_tokens", 0),
        )
        return result

    async def invoke_embedding(
        self,
        text: str,
        timeout: int = 5,
        model_id: Optional[str] = None,
    ) -> dict:
        """
        Invoke Vertex text embedding model.
        Returns: embedding, input_tokens, output_tokens, model_id, latency_ms, estimated_cost_usd
        """
        self._ensure_available()

        model = model_id or settings.VERTEX_EMBEDDING_MODEL_ID
        normalized_text = (text or "")[:8000]

        def _invoke() -> dict:
            embedding_model = self._get_embedding_model(model)
            embeddings = embedding_model.get_embeddings([normalized_text])
            if not embeddings:
                return {
                    "embedding": [],
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "model_id": model,
                }

            item = embeddings[0]
            vector = list(getattr(item, "values", []) or [])

            input_tokens = self._extract_embedding_tokens(item)
            if input_tokens <= 0:
                input_tokens = self._estimate_tokens(normalized_text)

            return {
                "embedding": vector,
                "input_tokens": input_tokens,
                "output_tokens": 0,
                "model_id": model,
            }

        result = await self._run_with_retry(
            operation_name="embedding_generate",
            operation_fn=_invoke,
            timeout=timeout,
        )

        result["estimated_cost_usd"] = self._calculate_cost(
            model,
            result.get("input_tokens", 0),
            result.get("output_tokens", 0),
        )
        return result

    # Compatibility aliases for old Bedrock call sites.
    async def invoke_claude(
        self,
        prompt: str,
        system_prompt: str = "",
        model_id: Optional[str] = None,
        max_tokens: int = 200,
        temperature: float = 0.0,
        timeout: int = 10,
    ) -> dict:
        return await self.invoke_gemini(
            prompt=prompt,
            system_prompt=system_prompt,
            model_id=model_id,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=timeout,
        )

    async def invoke_titan_embedding(self, text: str, timeout: int = 5) -> dict:
        return await self.invoke_embedding(text=text, timeout=timeout)

    async def _run_with_retry(
        self,
        operation_name: str,
        operation_fn: Callable[[], dict],
        timeout: int,
    ) -> dict:
        max_retries = max(settings.AI_MAX_RETRIES, 0)
        last_error: Optional[VertexAIClientError] = None

        for attempt in range(max_retries + 1):
            start_time = time.monotonic()
            try:
                loop = asyncio.get_running_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, operation_fn),
                    timeout=timeout,
                )
                result["latency_ms"] = int((time.monotonic() - start_time) * 1000)
                return result

            except asyncio.TimeoutError:
                last_error = VertexAIClientError(
                    f"{operation_name} timeout after {timeout}s",
                    retryable=True,
                    status_code=504,
                )

            except Exception as exc:
                classified = self._classify_exception(exc)
                if not classified.retryable:
                    raise classified
                last_error = classified

            if attempt < max_retries:
                backoff = min((2 ** attempt) + random.uniform(0, 1), 10)
                logger.warning(
                    "Vertex operation failed (op=%s, attempt=%d/%d): %s. Retrying in %.1fs",
                    operation_name,
                    attempt + 1,
                    max_retries + 1,
                    last_error,
                    backoff,
                )
                await asyncio.sleep(backoff)

        raise last_error or VertexAIClientError(
            f"{operation_name} failed after retries",
            retryable=False,
            status_code=502,
        )

    def _classify_exception(self, error: Exception) -> VertexAIClientError:
        if isinstance(error, VertexAIClientError):
            return error

        message = str(error)
        lowered = message.lower()

        if google_exceptions is not None:
            if isinstance(error, google_exceptions.PermissionDenied):
                return VertexAIClientError(message, retryable=False, status_code=403)
            if isinstance(
                error,
                (
                    google_exceptions.ResourceExhausted,
                    google_exceptions.ServiceUnavailable,
                    google_exceptions.DeadlineExceeded,
                    google_exceptions.InternalServerError,
                ),
            ):
                return VertexAIClientError(message, retryable=True, status_code=503)

        if isinstance(error, GoogleAuthError):
            return VertexAIClientError(message, retryable=False, status_code=503)

        if "permission" in lowered or "access denied" in lowered:
            return VertexAIClientError(message, retryable=False, status_code=403)

        if "quota" in lowered or "429" in lowered or "rate" in lowered:
            return VertexAIClientError(message, retryable=True, status_code=429)

        if "503" in lowered or "timeout" in lowered or "deadline" in lowered:
            return VertexAIClientError(message, retryable=True, status_code=503)

        return VertexAIClientError(message, retryable=False, status_code=500)

    @staticmethod
    def _extract_generated_text(response: Any) -> str:
        text = getattr(response, "text", None)
        if text:
            return text.strip()

        parts: list[str] = []
        candidates = getattr(response, "candidates", None) or []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            if content is None:
                continue
            candidate_parts = getattr(content, "parts", None) or []
            for part in candidate_parts:
                part_text = getattr(part, "text", "")
                if part_text:
                    parts.append(part_text)

        return "\n".join(parts).strip()

    def _extract_generation_usage(
        self,
        response: Any,
        request_text: str,
        output_text: str,
    ) -> tuple[int, int]:
        usage = getattr(response, "usage_metadata", None)

        input_tokens = 0
        output_tokens = 0

        if usage is not None:
            input_tokens = int(getattr(usage, "prompt_token_count", 0) or 0)
            output_tokens = int(getattr(usage, "candidates_token_count", 0) or 0)

            # Some SDK versions expose usage as dict-like payload.
            if input_tokens == 0 and isinstance(usage, dict):
                input_tokens = int(usage.get("prompt_token_count", 0) or 0)
                output_tokens = int(usage.get("candidates_token_count", 0) or 0)

        if input_tokens <= 0:
            input_tokens = self._estimate_tokens(request_text)
        if output_tokens < 0:
            output_tokens = 0
        if output_tokens == 0 and output_text:
            output_tokens = self._estimate_tokens(output_text)

        return input_tokens, output_tokens

    @staticmethod
    def _extract_embedding_tokens(item: Any) -> int:
        stats = getattr(item, "statistics", None)
        if stats is None:
            return 0

        token_count = getattr(stats, "token_count", 0)
        try:
            return int(token_count or 0)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        # Rough approximation for fallback accounting.
        return max(int(len(text or "") / 4), 1)

    @staticmethod
    def _calculate_cost(model_id: str, input_tokens: int, output_tokens: int) -> float:
        costs = MODEL_COSTS.get(model_id, {"input": 0.0002, "output": 0.0006})
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        return round(input_cost + output_cost, 8)


# Singleton instance
vertex_ai_client = VertexAIClient()
