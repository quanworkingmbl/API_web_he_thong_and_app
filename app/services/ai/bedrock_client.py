"""
AWS Bedrock Client Wrapper
- Retry logic với exponential backoff + jitter
- Timeout per operation type
- Cost tracking per request
- Error classification (retryable vs non-retryable)
"""

import json
import time
import random
import logging
from typing import Optional, Any
from datetime import datetime, date

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError, ReadTimeoutError, ConnectTimeoutError

from app.core.config import settings

logger = logging.getLogger(__name__)

# ==============================================================================
# COST CONSTANTS (per 1K tokens, USD) — Cập nhật theo bảng giá AWS
# ==============================================================================

MODEL_COSTS = {
    "anthropic.claude-3-haiku-20240307-v1:0": {
        "input": 0.00025,    # $0.25 / 1M input tokens
        "output": 0.00125,   # $1.25 / 1M output tokens
    },
    "anthropic.claude-3-sonnet-20240229-v1:0": {
        "input": 0.003,      # $3.00 / 1M input tokens
        "output": 0.015,     # $15.00 / 1M output tokens
    },
    "amazon.titan-embed-text-v2:0": {
        "input": 0.0001,     # $0.10 / 1M input tokens
        "output": 0.0,       # Embedding không có output tokens
    },
}


class BedrockClientError(Exception):
    """Base error for Bedrock operations."""
    def __init__(self, message: str, retryable: bool = False, status_code: int = 500):
        super().__init__(message)
        self.retryable = retryable
        self.status_code = status_code


class BedrockClient:
    """Singleton-style AWS Bedrock client with retry, timeout, and cost tracking."""

    _instance: Optional["BedrockClient"] = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            try:
                boto_config = BotoConfig(
                    region_name=settings.AWS_REGION,
                    retries={"max_attempts": 0},  # Tự quản lý retry
                )
                access_key = (settings.AWS_ACCESS_KEY_ID or "").strip()
                secret_key = (settings.AWS_SECRET_ACCESS_KEY or "").strip()

                client_kwargs: dict[str, Any] = {"config": boto_config}
                auth_mode = "iam_role"
                if access_key and secret_key:
                    client_kwargs["aws_access_key_id"] = access_key
                    client_kwargs["aws_secret_access_key"] = secret_key
                    auth_mode = "env_keys"

                self._client = boto3.client("bedrock-runtime", **client_kwargs)
                logger.info(
                    "BedrockClient initialized successfully (region=%s, auth=%s)",
                    settings.AWS_REGION,
                    auth_mode,
                )
            except Exception as e:
                logger.error("Failed to initialize BedrockClient: %s", e)
                self._client = None

    @property
    def is_available(self) -> bool:
        return self._client is not None

    # --------------------------------------------------------------------------
    # PUBLIC METHODS
    # --------------------------------------------------------------------------

    async def invoke_claude(
        self,
        prompt: str,
        system_prompt: str = "",
        model_id: Optional[str] = None,
        max_tokens: int = 200,
        temperature: float = 0.0,
        timeout: int = 10,
    ) -> dict:
        """
        Invoke Claude (Haiku or Sonnet) via Bedrock.
        Returns dict with keys: content, input_tokens, output_tokens, model_id, latency_ms
        """
        if not self.is_available:
            raise BedrockClientError("Bedrock client not initialized", retryable=False)

        model = model_id or settings.BEDROCK_MODERATION_MODEL_ID

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ],
        }
        if system_prompt:
            body["system"] = system_prompt

        return await self._invoke_with_retry(
            model_id=model,
            body=body,
            timeout=timeout,
            parse_fn=self._parse_claude_response,
        )

    async def invoke_titan_embedding(
        self,
        text: str,
        timeout: int = 5,
    ) -> dict:
        """
        Invoke Titan Embedding v2.
        Returns dict with keys: embedding (list[float]), input_tokens, model_id, latency_ms
        """
        if not self.is_available:
            raise BedrockClientError("Bedrock client not initialized", retryable=False)

        model = settings.BEDROCK_EMBEDDING_MODEL_ID

        body = {
            "inputText": text[:8000],  # Titan v2 limit
        }

        return await self._invoke_with_retry(
            model_id=model,
            body=body,
            timeout=timeout,
            parse_fn=self._parse_titan_response,
        )

    # --------------------------------------------------------------------------
    # INTERNAL — RETRY + INVOKE
    # --------------------------------------------------------------------------

    async def _invoke_with_retry(
        self,
        model_id: str,
        body: dict,
        timeout: int,
        parse_fn,
    ) -> dict:
        """Invoke Bedrock with exponential backoff + jitter retry."""
        max_retries = settings.AI_MAX_RETRIES
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                start_time = time.monotonic()

                # Synchronous boto3 call (FastAPI runs in threadpool for sync)
                import asyncio
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self._client.invoke_model(
                        modelId=model_id,
                        contentType="application/json",
                        accept="application/json",
                        body=json.dumps(body),
                    )
                )

                latency_ms = int((time.monotonic() - start_time) * 1000)

                # Parse response
                response_body = json.loads(response["body"].read())
                result = parse_fn(response_body)
                result["model_id"] = model_id
                result["latency_ms"] = latency_ms

                # Tính cost
                cost = self._calculate_cost(
                    model_id,
                    result.get("input_tokens", 0),
                    result.get("output_tokens", 0),
                )
                result["estimated_cost_usd"] = cost

                logger.info(
                    "Bedrock invoke success: model=%s latency=%dms tokens_in=%d tokens_out=%d cost=$%.6f",
                    model_id, latency_ms,
                    result.get("input_tokens", 0),
                    result.get("output_tokens", 0),
                    cost,
                )

                return result

            except (ReadTimeoutError, ConnectTimeoutError) as e:
                last_error = BedrockClientError(f"Timeout after {timeout}s: {e}", retryable=True, status_code=504)
                logger.warning("Bedrock timeout (attempt %d/%d): %s", attempt + 1, max_retries + 1, e)

            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "")
                status_code = e.response.get("ResponseMetadata", {}).get("HTTPStatusCode", 500)

                if self._is_retryable_error(error_code, status_code):
                    last_error = BedrockClientError(str(e), retryable=True, status_code=status_code)
                    logger.warning("Bedrock retryable error (attempt %d/%d): %s", attempt + 1, max_retries + 1, e)
                else:
                    # Non-retryable (4xx client errors)
                    raise BedrockClientError(str(e), retryable=False, status_code=status_code)

            except Exception as e:
                logger.error("Bedrock unexpected error: %s", e)
                raise BedrockClientError(f"Unexpected error: {e}", retryable=False)

            # Exponential backoff + jitter
            if attempt < max_retries:
                backoff = min(2 ** attempt + random.uniform(0, 1), 10)
                logger.info("Retrying in %.1fs...", backoff)
                import asyncio
                await asyncio.sleep(backoff)

        raise last_error or BedrockClientError("Max retries exceeded", retryable=False)

    # --------------------------------------------------------------------------
    # PARSERS
    # --------------------------------------------------------------------------

    @staticmethod
    def _parse_claude_response(response_body: dict) -> dict:
        """Parse Claude response format."""
        content_blocks = response_body.get("content", [])
        text = ""
        for block in content_blocks:
            if block.get("type") == "text":
                text += block.get("text", "")

        usage = response_body.get("usage", {})
        return {
            "content": text.strip(),
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
        }

    @staticmethod
    def _parse_titan_response(response_body: dict) -> dict:
        """Parse Titan Embedding response."""
        return {
            "embedding": response_body.get("embedding", []),
            "input_tokens": response_body.get("inputTextTokenCount", 0),
            "output_tokens": 0,
        }

    # --------------------------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------------------------

    @staticmethod
    def _is_retryable_error(error_code: str, status_code: int) -> bool:
        """Only retry timeout, 429, 5xx. Never retry 4xx client errors."""
        if status_code == 429:  # Throttling
            return True
        if status_code >= 500:  # Server errors
            return True
        if error_code in ("ThrottlingException", "ServiceUnavailableException", "InternalServerException"):
            return True
        return False

    @staticmethod
    def _calculate_cost(model_id: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost in USD."""
        costs = MODEL_COSTS.get(model_id, {"input": 0.001, "output": 0.005})
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        return round(input_cost + output_cost, 8)


# Singleton instance
bedrock_client = BedrockClient()
