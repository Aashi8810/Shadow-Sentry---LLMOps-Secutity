"""
Central configuration for Shadow Sentry.
All thresholds and tunables live here so they can be adjusted live during a demo
without digging through the codebase.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="SHADOW_", extra="ignore")

    # --- App ---
    app_name: str = "Shadow Sentry"
    debug: bool = True

    # --- LLM backend (Groq) ---
    # Groq's API is OpenAI-compatible: POST {base_url}/chat/completions
    groq_api_key: str = ""
    groq_base_url: str = "https://api.groq.com/openai/v1"
    # Default model is intentionally left generic/configurable — set the
    # exact model name via SHADOW_GROQ_MODEL in .env once decided.
    # Common options: "llama-3.1-8b-instant", "llama-3.3-70b-versatile"
    groq_model: str = "llama-3.1-8b-instant"
    groq_timeout_seconds: float = 60.0

    # --- Detection model (also via Groq, can be a different/cheaper model) ---
    # Used later (Day 2+) as a stand-in classifier role similar to Llama Guard.
    groq_guard_model: str = "llama-3.1-8b-instant"

    # --- Database ---
    database_url: str = "sqlite:///./shadow_sentry.db"

    # --- Risk scoring weights (0-100 scale contributions) ---
    weight_regex_match: int = 40
    weight_llama_guard_unsafe: int = 50
    weight_injection_pattern: int = 35
    weight_pii_present: int = 25
    weight_document_injection: int = 45

    # --- Risk level thresholds ---
    threshold_low_max: int = 24       # 0-24   -> LOW
    threshold_medium_max: int = 59    # 25-59  -> MEDIUM
    threshold_high_max: int = 84      # 60-84  -> HIGH
    # 85-100 -> BLOCKED (also blocked if explicit hard-block rule fires)
    block_threshold: int = 85

    # --- Rate limiting ---
    rate_limit_per_minute: int = 20

    # --- Detection toggles (useful to flip off live during demo) ---
    enable_regex_filter: bool = True
    enable_llama_guard: bool = True
    enable_injection_patterns: bool = True
    enable_pii_detection: bool = True


settings = Settings()
