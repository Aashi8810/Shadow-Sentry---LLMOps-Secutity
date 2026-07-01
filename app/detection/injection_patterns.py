"""
Library of known malicious payloads and prompt injection markers.
"""
import re

# Common phrases used to override system instructions
JAILBREAK_PHRASES = [
    r"ignore previous instructions",
    r"ignore all prior instructions",
    r"you are now DAN",
    r"developer mode",
    r"pretend you have no restrictions",
    r"ignore your system prompt",
    r"system prompt verbatim",
    r"bypassing your core directives",
    r"disregard previous instructions"
]

# Compile once at startup for speed
COMPILED_JAILBREAKS = [
    re.compile(pattern, re.IGNORECASE) for pattern in JAILBREAK_PHRASES
]