"""
Fast first-pass filter using regex.
"""
from app.detection.injection_patterns import COMPILED_JAILBREAKS

def scan_prompt_regex(prompt: str) -> list[str]:
    """
    Scans the prompt against known jailbreak patterns.
    Returns a list of triggered reasons (empty if clean).
    """
    reasons = []
    for pattern in COMPILED_JAILBREAKS:
        if pattern.search(prompt):
            reasons.append(f"regex_match: {pattern.pattern}")
    return reasons