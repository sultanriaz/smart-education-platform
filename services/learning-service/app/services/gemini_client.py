from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import re
import time
from typing import Any

from pydantic import BaseModel, Field

from app.core.config import settings

logger = logging.getLogger("learning-service.gemini")

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


class ExtractedTopicsSchema(BaseModel):
    topics: list[str] = Field(
        default_factory=list,
        description="Extracted chapters, modules, or key study topics in sequential order",
    )
    summary: str = Field(
        default="",
        description="Brief high-level summary of the document's academic syllabus or subject matter",
    )


def deterministic_embedding(text: str, dim: int = 768) -> list[float]:
    """Generates a deterministic, normalized 768-dimensional vector from text."""
    seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)
    vec: list[float] = []
    for i in range(dim):
        val = math.sin((seed % 100000) + (i + 1) * 0.732)
        vec.append(val)
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [round(x / norm, 6) for x in vec]


class GeminiClient:
    """Resilient client for Google Gemini API with retries, structured schema, and fallback."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        self.embedding_model = settings.GEMINI_EMBEDDING_MODEL or "text-embedding-004"
        self.chat_model = settings.GEMINI_CHAT_MODEL or "gemini-2.0-flash"
        self._client = None
        if self.api_key and genai is not None:
            try:
                self._client = genai.Client(api_key=self.api_key)
                logger.info("Initialized Google GenAI client successfully.")
            except Exception as e:
                logger.warning("Failed to initialize Google GenAI client: %s. Using fallback.", e)

    def is_live(self) -> bool:
        return self._client is not None

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate 768-dimensional embeddings for a list of text strings with retries and fallback."""
        if not texts:
            return []

        if self._client is not None and types is not None:
            results: list[list[float]] = []
            for text in texts:
                emb = self._embed_with_retry(text)
                if emb:
                    results.append(emb)
                else:
                    results.append(deterministic_embedding(text, 768))
            return results

        return [deterministic_embedding(t, 768) for t in texts]

    def generate_embedding(self, text: str) -> list[float]:
        """Generate a single 768-dimensional embedding."""
        embs = self.generate_embeddings([text])
        return embs[0] if embs else deterministic_embedding(text, 768)

    def _embed_with_retry(self, text: str, max_retries: int = 3) -> list[float] | None:
        """Embed a single text snippet with exponential backoff on transient errors."""
        backoff = 1.0
        for attempt in range(max_retries):
            try:
                response = self._client.models.embed_content(
                    model=self.embedding_model,
                    contents=text,
                )
                if response and response.embeddings:
                    first = response.embeddings[0]
                    if hasattr(first, "values") and first.values:
                        return list(first.values)
                return None
            except Exception as exc:
                logger.warning(
                    "Gemini embed_content attempt %s/%s failed: %s", attempt + 1, max_retries, exc
                )
                if attempt < max_retries - 1:
                    time.sleep(backoff)
                    backoff *= 2.0
        return None

    def extract_topics(self, text: str, filename: str) -> list[str]:
        """Extract structured chapters and topics using Gemini with fallback heuristics."""
        if not text or not text.strip():
            return ["Overview"]

        # Truncate preview text for prompt if excessively long
        preview_text = text[:12000]

        if self._client is not None and types is not None:
            for attempt in range(2):
                try:
                    prompt = (
                        f"You are an academic curriculum analyzer. Extract the main chapters, modules, "
                        f"and key study topics from the following educational material ({filename}).\n\n"
                        f"Content excerpt:\n{preview_text}\n\n"
                        f"Return a structured list of clear, informative topic titles."
                    )
                    config = types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=ExtractedTopicsSchema,
                        temperature=0.2,
                    )
                    response = self._client.models.generate_content(
                        model=self.chat_model,
                        contents=prompt,
                        config=config,
                    )
                    if response and response.text:
                        data = json.loads(response.text)
                        topics = data.get("topics", [])
                        if isinstance(topics, list) and topics:
                            clean_topics = [str(t).strip() for t in topics if str(t).strip()]
                            if clean_topics:
                                return clean_topics[:25]
                except Exception as exc:
                    logger.warning("Gemini extract_topics attempt %s failed: %s", attempt + 1, exc)
                    time.sleep(1.0)

        # Fallback heuristic topic extraction
        return self._heuristic_extract_topics(text, filename)

    def _heuristic_extract_topics(self, text: str, filename: str) -> list[str]:
        """Extract chapter/topic headings using regex patterns and structural clues."""
        topics: list[str] = []
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        heading_patterns = [
            re.compile(r"^(chapter\s+\d+[:\s\.-].*)$", re.IGNORECASE),
            re.compile(r"^(module\s+\d+[:\s\.-].*)$", re.IGNORECASE),
            re.compile(r"^(unit\s+\d+[:\s\.-].*)$", re.IGNORECASE),
            re.compile(r"^(lesson\s+\d+[:\s\.-].*)$", re.IGNORECASE),
            re.compile(r"^(part\s+[ivxlcdm\d]+[:\s\.-].*)$", re.IGNORECASE),
            re.compile(r"^(#{1,3}\s+.*)$"),  # Markdown headers
            re.compile(r"^(\d+\.\d*\s+[A-Z].*)$"),  # 1.1 Topic Name
        ]

        for line in lines[:300]:
            for pat in heading_patterns:
                m = pat.match(line)
                if m:
                    clean = re.sub(r"^[#\s]+", "", m.group(1)).strip()
                    if clean and len(clean) < 120 and clean not in topics:
                        topics.append(clean)
                    break
            if len(topics) >= 15:
                break

        if not topics:
            # Fallback: create topics from first meaningful headers or file name
            base_name = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").title()
            topics = [f"{base_name} - Introduction", f"{base_name} - Core Concepts", f"{base_name} - Summary & Review"]

        return topics


_gemini_client_instance: GeminiClient | None = None


def get_gemini_client() -> GeminiClient:
    global _gemini_client_instance
    if _gemini_client_instance is None:
        _gemini_client_instance = GeminiClient()
    return _gemini_client_instance
