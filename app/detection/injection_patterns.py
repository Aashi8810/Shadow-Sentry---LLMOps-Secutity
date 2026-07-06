"""
Library of known malicious payloads and prompt injection markers.
"""
import re

JAILBREAK_PHRASES = [
    # Captures "ignore instructions", "ignore all previous instructions", "ignore prior instructions"
    r"ignore.*\binstructions\b",
    r"disregard.*\binstructions\b",
    r"bypass.*\brestrictions\b",
    r"clear.*\binstructions\b",
    
    # Common Jailbreak Persona Initializations
    r"\byou\b.*are.*\bnow\b.*dan\b",
    r"\bdeveloper\b.*\bmode\b",
    r"pretend.*\bno\b.*\brestrictions\b",
    
    # Prompt Leaking Targets
    r"system.*\bprompt\b.*\bverbatim\b",
    r"system.*\binstructions\b.*\bverbatim\b",
    r"repeat.*\bwords\b.*\babove\b",
    r"output.*\binitial\b.*\binstructions\b"
]

COMPILED_JAILBREAKS = [
    re.compile(pattern, re.IGNORECASE) for pattern in JAILBREAK_PHRASES
]