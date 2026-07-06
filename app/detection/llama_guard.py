"""
Integration with Llama Guard 3 for semantic safety classification.
"""
import logging
from app.config import settings
from app.llm.client import generate, LLMClientError

logger = logging.getLogger(__name__)

async def check_prompt_safety(prompt: str) -> tuple[bool, str]:
    """
    Calls Llama Guard 3 to classify the prompt, using formal structural framing.
    """
    if not settings.enable_llama_guard:
        return False, ""

    # Wrap the untrusted input within official Meta structural tags
    # This signals to the guard model exactly where the untrusted user boundary is
    formatted_guard_prompt = f"""<BEGIN CONVERSATION>
User: {prompt}
<END CONVERSATION>"""

    try:
        guard_response = await generate(
            prompt=formatted_guard_prompt,
            model=settings.groq_guard_model
        )
        
        result_text = guard_response.strip().lower()
        
        # If Llama Guard flags it as unsafe
        if "unsafe" in result_text:
            parts = result_text.split("\n")
            category = parts[1].strip() if len(parts) > 1 else "prompt_attack"
            return True, f"llama_guard_flag: {category}"
            
        return False, ""
        
    except LLMClientError as e:
        logger.error(f"Llama Guard check failed: {e}")
        return False, "llama_guard_error: service_unavailable"