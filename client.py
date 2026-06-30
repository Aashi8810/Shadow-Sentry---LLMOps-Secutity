"""
Thin wrapper around the LLM backend — Groq's OpenAI-compatible chat completions API.

Keeping this isolated means later we can swap backends (OpenAI/Anthropic/local)
without touching route logic. Day 2's llama_guard.py-equivalent classifier will
reuse the same low-level call function with a different model/prompt.
"""
import httpx

from app.config import settings


class LLMClientError(Exception):
    pass


async def generate(prompt: str, model: str | None = None, system: str | None = None) -> str:
    """
    Send a prompt to Groq's chat completions endpoint and return the text response.
    Raises LLMClientError on failure (missing key, network error, bad status)
    so routes can decide how to handle it (e.g. 502 to the client).
    """
    if not settings.groq_api_key:
        raise LLMClientError(
            "GROQ_API_KEY is not set. Add SHADOW_GROQ_API_KEY to your .env file."
        )

    url = f"{settings.groq_base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model or settings.groq_model,
        "messages": messages,
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=settings.groq_timeout_seconds) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
    except httpx.HTTPStatusError as e:
        # Surface Groq's error body when possible — very helpful for debugging
        # bad API keys / decommissioned model names during setup.
        detail = ""
        try:
            detail = e.response.json().get("error", {}).get("message", "")
        except Exception:
            detail = e.response.text[:300]
        raise LLMClientError(f"Groq request failed ({e.response.status_code}): {detail}") from e
    except httpx.HTTPError as e:
        raise LLMClientError(f"Groq request failed: {e}") from e
    except (KeyError, IndexError) as e:
        raise LLMClientError(f"Unexpected Groq response shape: {e}") from e
