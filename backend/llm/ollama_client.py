# llm/ollama_client.py
import json
import logging
from collections.abc import Generator

import httpx

from config import settings

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """\
You are a helpful assistant.

Behavior rules:
1. If the user input is a greeting (e.g., "hi", "hello", "hey"):
   - Respond with a friendly greeting.
   - Briefly mention that you can help answer questions based on the provided documents.

2. If the user asks a question:
   - Answer using ONLY the context provided below.
   - If the answer is not present in the context, say:
     "I don't have enough information in the provided documents to answer this."

3. Do NOT use outside knowledge for answering questions.

Context:
{context}

User Input: {question}

Answer:"""


class OllamaClient:
    def __init__(self, base_url: str, model: str):
        self._base_url = base_url.rstrip("/")
        self._model = model
        logger.info("OllamaClient ready — model: %s at %s", model, base_url)

    def _build_prompt(self, question: str, context: str) -> str:
        return PROMPT_TEMPLATE.format(context=context, question=question)

    def generate(self, question: str, context: str) -> str:
        """Sync response — /ask endpoint के लिए।"""
        prompt = self._build_prompt(question, context)

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self._base_url}/api/generate",
                json={"model": self._model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            data = response.json()
            return data["response"].strip()

    def stream(self, question: str, context: str) -> Generator[str, None, None]:
        """
        Token-by-token streaming — /ask/stream endpoint के लिए।
        Ollama newline-delimited JSON return करता है।
        """
        prompt = self._build_prompt(question, context)

        with httpx.Client(timeout=120.0) as client:
            with client.stream(
                "POST",
                f"{self._base_url}/api/generate",
                json={"model": self._model, "prompt": prompt, "stream": True},
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
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