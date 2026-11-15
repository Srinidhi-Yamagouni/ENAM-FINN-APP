"""Small, deterministic evidence gate used before research claims reach the UI."""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Check:
    value: float
    source_text: str
    verified: bool
    reason: str


def verify_number(value: float, source_text: str, tolerance: float = 0.001) -> Check:
    """Keep a numeric claim only when the exact value occurs in its source span."""
    numbers = []
    for token in re.findall(r"-?\d[\d,]*(?:\.\d+)?", source_text):
        numbers.append(float(token.replace(",", "")))
    verified = any(abs(value - candidate) <= tolerance for candidate in numbers)
    return Check(value, source_text, verified, "matched source span" if verified else "value absent from source span")


def grounded_claim(value: float, source: str, citation: dict) -> dict | None:
    check = verify_number(value, source)
    if not check.verified:
        return None
    return {"value": value, "citation": citation, "verified": True}
