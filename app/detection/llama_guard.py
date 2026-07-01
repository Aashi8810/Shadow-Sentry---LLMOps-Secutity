"""
Integration with Llama Guard 3 for semantic safety classification.
"""
import logging
from app.config import settings
from app.llm.client import generate, LLMClientError

logger = logging.getLogger(__name__)

async def check_prompt_safety(prompt: str) -> tuple[bool, str]:
    """
    Calls Llama Guard to classify the prompt.
    Returns (is_unsafe: bool, reason: str)
    """
    if not settings.enable_llama_guard:
        return False, ""

    try:
        # We pass the user's prompt directly to the guard model.
        # Ensure SHADOW_GROQ_GUARD_MODEL is set to "llama-guard-3-8b" in your .env
        guard_response = await generate(
            prompt=prompt,
            model=settings.groq_guard_model
        )
        
        # Llama Guard typically outputs "safe" or "unsafe\n<Category>"
        result_text = guard_response.strip().lower()
        
        if result_text.startswith("unsafe"):
            parts = result_text.split("\n")
            category = parts[1].strip() if len(parts) > 1 else "unknown_category"
            return True, f"llama_guard_flag: {category}"
            
        return False, ""
        
    except LLMClientError as e:
        logger.error(f"Llama Guard check failed: {e}")
        # In a real system, you might fail closed. For demo stability, we fail open.
        return False, "llama_guard_error: service_unavailable"