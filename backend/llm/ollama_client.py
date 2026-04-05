import json
import logging
from collections.abc import AsyncGenerator

import httpx

from config import settings

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """\
You are a helpful assistant. Answer the question using ONLY the context below.
If the answer is not present in the context, say:
"I don't have enough information in the provided documents to answer this."

Context:
{context}

Question: {question}

Answer:"""


class OllamaClient:
    def __init__(self, base_url: str, model: str):
        self._base_url = base_url.rstrip("/")
        self._model = model
        logger.info("OllamaClient ready — model: %s at %s", model, base_url)

    def _build_prompt(self, question: str, context: str) -> str:
        return PROMPT_TEMPLATE.format(context=context, question=question)

    async def generate(self, question: str, context: str) -> str:
        prompt = self._build_prompt(question, context)

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self._base_url}/api/generate",
                json={"model": self._model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            data = response.json()
            return data["response"].strip() if "response" in data else ""

    async def stream(self, question: str, context: str) -> AsyncGenerator[str, None]:
        prompt = self._build_prompt(question, context)

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self._base_url}/api/generate",
                json={"model": self._model, "prompt": prompt, "stream": True},
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("response", "")
                        if token:
                            yield token
                        if chunk.get("done"):
                            break
                    except json.JSONDecodeError:
                        logger.warning("Could not parse line: %s", line)
                        continue