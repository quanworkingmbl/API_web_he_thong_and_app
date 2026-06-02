"""
Vertex AI Client Wrapper (google-genai SDK >= 1.66.0)
- Uses google.genai.Client with vertexai=True instead of deprecated vertexai SDK
- Retry logic with exponential backoff + jitter
- Timeout per operation type
- Cost estimation per request
- Error classification (retryable vs non-retryable)
"""

import asyncio
import logging
import random
import time
from pathlib import Path
from typing import Any, Callable, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types as genai_types
    from google.oauth2 import service_account as google_sa
    from google.api_core import exceptions as google_exceptions
    from google.auth.exceptions import GoogleAuthError

    VERTEX_IMPORT_ERROR = None
except Exception as import_error:  # pragma: no cover
    genai = None
    genai_types = None
    google_sa = None
    google_exceptions = None
    GoogleAuthError = Exception
    VERTEX_IMPORT_ERROR = import_error


# Approximate public pricing (USD per 1K tokens). Update when pricing changes.
MODEL_COSTS = {
    "gemini-2.5-flash": {"input": 0.000075, "output": 0.00030},
    "gemini-2.5-pro": {"input": 0.00125, "output": 0.00500},
    "gemini-2.0-flash": {"input": 0.000075, "output": 0.00030},
    "gemini-2.0-flash-001": {"input": 0.000075, "output": 0.00030},
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
    """Singleton Vertex AI client using google-genai SDK with retry, timeout, and cost tracking."""

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
        self._client: Optional[Any] = None

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

        if location.lower() == "global":
            logger.warning(
                "VERTEX_LOCATION=global is not supported; falling back to us-central1"
            )
            location = "us-central1"

        if not project_id:
            raise VertexAIClientError(
                "VERTEX_PROJECT_ID is required to use Vertex AI",
                retryable=False,
                status_code=503,
            )

        # Load service account credentials if path provided
        credentials = None
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

            try:
                credentials = google_sa.Credentials.from_service_account_file(
                    str(resolved),
                    scopes=["https://www.googleapis.com/auth/cloud-platform"],
                )
            except Exception as exc:
                raise VertexAIClientError(
                    f"Failed to load service account: {exc}",
                    retryable=False,
                    status_code=503,
                ) from exc

        # Build google-genai client with Vertex AI backend
        try:
            client_kwargs: dict = {
                "vertexai": True,
                "project": project_id,
                "location": location,
            }
            if credentials is not None:
                client_kwargs["credentials"] = credentials

            self._client = genai.Client(**client_kwargs)
        except Exception as exc:
            raise VertexAIClientError(
                f"Failed to create Vertex AI client: {exc}",
                retryable=False,
                status_code=503,
            ) from exc

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

    async def invoke_gemini(
        self,
        prompt: str,
        system_prompt: str = "",
        model_id: Optional[str] = None,
        max_tokens: int = 200,
        temperature: float = 0.0,
        timeout: int = 10,
        json_mode: bool = False,
    ) -> dict:
        """
        Invoke Gemini model via Vertex AI (google-genai SDK).
        json_mode=True forces response_mime_type='application/json' — use for structured outputs.
        Returns: content, input_tokens, output_tokens, model_id, latency_ms, estimated_cost_usd
        """
        self._ensure_available()

        model = model_id or settings.VERTEX_MODERATION_MODEL_ID
        contents = prompt.strip()

        def _invoke() -> dict:
            config_kwargs: dict = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            if system_prompt:
                config_kwargs["system_instruction"] = system_prompt
            if json_mode:
                config_kwargs["response_mime_type"] = "application/json"
                # Disable thinking mode for JSON output — thinking + JSON mime type
                # causes empty responses in Gemini 2.5 Flash
                config_kwargs["thinking_config"] = genai_types.ThinkingConfig(thinking_budget=0)

            config = genai_types.GenerateContentConfig(**config_kwargs)

            response = self._client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )

            content = self._extract_text(response)

            # Extract token usage from response metadata
            usage = getattr(response, "usage_metadata", None)
            input_tokens = int(getattr(usage, "prompt_token_count", 0) or 0) if usage else 0
            output_tokens = int(getattr(usage, "candidates_token_count", 0) or 0) if usage else 0

            if input_tokens <= 0:
                input_tokens = self._estimate_tokens(contents + (system_prompt or ""))
            if output_tokens == 0 and content:
                output_tokens = self._estimate_tokens(content)

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

    async def invoke_gemini_multimodal(
        self,
        prompt: str,
        image_urls: list[str],
        system_prompt: str = "",
        model_id: Optional[str] = None,
        max_tokens: int = 300,
        temperature: float = 0.0,
        timeout: int = 20,
        json_mode: bool = False,
        max_images: int = 5,
    ) -> dict:
        """
        Invoke Gemini với multimodal input (text + images).

        Args:
            prompt:       Nội dung text prompt
            image_urls:   Danh sách URL ảnh cần phân tích (tối đa max_images)
            system_prompt: System instruction
            model_id:     Model ID (mặc định: VERTEX_MODERATION_MODEL_ID)
            max_tokens:   Max output tokens
            temperature:  Sampling temperature (0 = deterministic)
            timeout:      Timeout giây (cao hơn invoke_gemini vì phải download ảnh)
            json_mode:    True = yêu cầu JSON response
            max_images:   Giới hạn số ảnh gửi lên (mặc định 5, tiết kiệm cost)

        Returns:
            dict: content, input_tokens, output_tokens, model_id, latency_ms,
                  estimated_cost_usd, images_analyzed (int)
        """
        self._ensure_available()

        model = model_id or settings.VERTEX_MODERATION_MODEL_ID

        # Download ảnh song song (asyncio.gather)
        valid_urls = [u for u in (image_urls or []) if u and u.startswith("http")][:max_images]
        image_parts: list[dict] = []

        if valid_urls:
            fetch_tasks = [self._fetch_image_as_base64(url) for url in valid_urls]
            fetch_results = await asyncio.gather(*fetch_tasks, return_exceptions=True)
            for fetch_result in fetch_results:
                if isinstance(fetch_result, dict) and fetch_result.get("data"):
                    image_parts.append(fetch_result)

        images_analyzed = len(image_parts)
        logger.info("[Multimodal] Prompt=%d chars, Images requested=%d, fetched=%d",
                    len(prompt), len(valid_urls), images_analyzed)

        def _invoke() -> dict:
            config_kwargs: dict = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            if system_prompt:
                config_kwargs["system_instruction"] = system_prompt
            if json_mode:
                config_kwargs["response_mime_type"] = "application/json"
                config_kwargs["thinking_config"] = genai_types.ThinkingConfig(thinking_budget=0)

            config = genai_types.GenerateContentConfig(**config_kwargs)

            # Build multipart contents: text + image parts
            # google-genai SDK expects list of Part objects
            parts: list = [genai_types.Part.from_text(prompt.strip())]
            for img in image_parts:
                parts.append(
                    genai_types.Part.from_bytes(
                        data=img["data"],
                        mime_type=img["mime_type"],
                    )
                )

            response = self._client.models.generate_content(
                model=model,
                contents=parts,
                config=config,
            )

            content = self._extract_text(response)

            usage = getattr(response, "usage_metadata", None)
            input_tokens = int(getattr(usage, "prompt_token_count", 0) or 0) if usage else 0
            output_tokens = int(getattr(usage, "candidates_token_count", 0) or 0) if usage else 0

            if input_tokens <= 0:
                # Rough estimate: text tokens + ~256 tokens per image
                input_tokens = self._estimate_tokens(prompt + (system_prompt or "")) + images_analyzed * 256
            if output_tokens == 0 and content:
                output_tokens = self._estimate_tokens(content)

            return {
                "content": content,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "model_id": model,
                "images_analyzed": images_analyzed,
            }

        result = await self._run_with_retry(
            operation_name="gemini_multimodal",
            operation_fn=_invoke,
            timeout=timeout,
        )

        result["estimated_cost_usd"] = self._calculate_cost(
            model,
            result.get("input_tokens", 0),
            result.get("output_tokens", 0),
        )
        result.setdefault("images_analyzed", images_analyzed)
        return result

    async def _fetch_image_as_base64(self, url: str) -> dict:
        """
        Download ảnh từ URL và trả về bytes để gửi vào Gemini multimodal.
        Dùng httpx (đã có trong requirements) thay vì aiohttp.

        Returns:
            dict: {"data": bytes, "mime_type": str} hoặc {} nếu thất bại
        """
        import httpx

        SUPPORTED_MIMES = {
            "image/jpeg", "image/jpg", "image/png", "image/webp",
            "image/gif", "image/bmp",
        }
        MAX_SIZE_BYTES = 4 * 1024 * 1024  # 4MB limit per image

        try:
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code != 200:
                    logger.warning("[Multimodal] Image fetch failed url=%s status=%d", url, resp.status_code)
                    return {}

                content_type = resp.headers.get("content-type", "").split(";")[0].strip().lower()
                # Fallback mime detection from URL extension
                if content_type not in SUPPORTED_MIMES:
                    ext = url.rsplit(".", 1)[-1].lower() if "." in url else ""
                    ext_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
                               "webp": "image/webp", "gif": "image/gif", "bmp": "image/bmp"}
                    content_type = ext_map.get(ext, "image/jpeg")

                if content_type not in SUPPORTED_MIMES:
                    logger.warning("[Multimodal] Unsupported image type url=%s mime=%s", url, content_type)
                    return {}

                raw = resp.content
                if len(raw) > MAX_SIZE_BYTES:
                    logger.warning("[Multimodal] Image too large (%d bytes), skipping: %s", len(raw), url)
                    return {}

                return {"data": raw, "mime_type": content_type}

        except httpx.TimeoutException:
            logger.warning("[Multimodal] Timeout downloading image: %s", url)
            return {}
        except Exception as exc:
            logger.warning("[Multimodal] Error fetching image %s: %s", url, exc)
            return {}




    async def invoke_embedding(
        self,
        text: str,
        timeout: int = 5,
        model_id: Optional[str] = None,
    ) -> dict:
        """
        Invoke Vertex text embedding model via google-genai SDK.
        Returns: embedding, input_tokens, output_tokens, model_id, latency_ms, estimated_cost_usd
        """
        self._ensure_available()

        model = model_id or settings.VERTEX_EMBEDDING_MODEL_ID
        normalized_text = (text or "")[:8000]

        def _invoke() -> dict:
            response = self._client.models.embed_content(
                model=model,
                contents=normalized_text,
            )

            embeddings = getattr(response, "embeddings", None) or []
            if not embeddings:
                return {
                    "embedding": [],
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "model_id": model,
                }

            vector = list(getattr(embeddings[0], "values", []) or [])
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

    # Compatibility aliases for old call sites
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
    def _extract_text(response: Any) -> str:
        """Extract text from google-genai response object."""
        # Primary: use .text property
        text = getattr(response, "text", None)
        if text:
            return text.strip()

        # Fallback: iterate candidates → content → parts
        parts: list[str] = []
        candidates = getattr(response, "candidates", None) or []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            if content is None:
                continue
            for part in getattr(content, "parts", None) or []:
                part_text = getattr(part, "text", "")
                if part_text:
                    parts.append(part_text)

        return "\n".join(parts).strip()

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Rough token count approximation for fallback accounting."""
        return max(int(len(text or "") / 4), 1)

    @staticmethod
    def _calculate_cost(model_id: str, input_tokens: int, output_tokens: int) -> float:
        # Exact match first, then prefix match for versioned models
        costs = MODEL_COSTS.get(model_id)
        if costs is None:
            for key in MODEL_COSTS:
                if model_id.startswith(key):
                    costs = MODEL_COSTS[key]
                    break
        if costs is None:
            costs = {"input": 0.0002, "output": 0.0006}

        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        return round(input_cost + output_cost, 8)


# Singleton instance
vertex_ai_client = VertexAIClient()
