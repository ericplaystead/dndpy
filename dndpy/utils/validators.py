"""
Generic validators used by rulesets and CLI prompts.
Each validator returns (coerced_value, error_message|None).
"""
import re
from typing import Any, Optional

DICE_RE = re.compile(r'^([1-9]\d*)d([1-9]\d*)([+-]\d+)?$')


def validate_nonempty(raw: Optional[str]) -> tuple[str, Optional[str]]:
    v = (raw or '').strip()
    if not v:
        return '', 'Cannot be empty'
    return v, None


def validate_int(raw: str) -> tuple[Optional[int], Optional[str]]:
    try:
        return int(raw.strip()), None
    except (ValueError, AttributeError):
        return None, 'Must be a whole number'


def validate_positive_int(raw: str) -> tuple[Optional[int], Optional[str]]:
    v, err = validate_int(raw)
    if err:
        return None, err
    if v <= 0:
        return None, 'Must be a positive number'
    return v, None


def validate_nonneg_int(raw: str) -> tuple[Optional[int], Optional[str]]:
    v, err = validate_int(raw)
    if err:
        return None, err
    if v < 0:
        return None, 'Cannot be negative'
    return v, None


def validate_dice_str(raw: str) -> tuple[Optional[str], Optional[str]]:
    v = (raw or '').strip()
    if not DICE_RE.match(v):
        return None, 'Must be dice notation like "2d6" or "1d8+2"'
    return v, None


def validate_choice(choices: list[str], case_sensitive: bool = False):
    """Returns a validator function that checks membership in a list."""
    def _validate(raw: Optional[str]) -> tuple[Optional[str], Optional[str]]:
        s = (raw or '').strip()
        v = s if case_sensitive else s.lower()
        pool = choices if case_sensitive else [c.lower() for c in choices]
        if v not in pool:
            return None, f'Must be one of: {", ".join(choices)}'
        idx = pool.index(v)
        return choices[idx], None
    return _validate


def validate_optional_int(raw: str) -> tuple[Optional[int], Optional[str]]:
    """Like validate_int but allows empty string (returns None, None)."""
    if not (raw or '').strip():
        return None, None
    return validate_int(raw)
