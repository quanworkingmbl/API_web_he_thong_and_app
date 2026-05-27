"""Compatibility shim.

The AI provider has moved from AWS Bedrock to Google Vertex AI.
Keep old import paths working while existing modules are migrated.
"""

from app.services.ai.vertex_client import VertexAIClientError as BedrockClientError
from app.services.ai.vertex_client import vertex_ai_client as bedrock_client

