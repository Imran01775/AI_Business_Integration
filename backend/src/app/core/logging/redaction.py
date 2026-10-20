"""PII redaction for structured logs (R-SEC-05, doc 22 §1.6)."""

from __future__ import annotations

import re
from typing import Any

_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
_PHONE_BD = re.compile(r"\b(?:\+?88)?01[3-9]\d{8}\b")
_BEARER = re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE)
_CARDISH = re.compile(r"\b(?:\d[ -]*?){13,19}\b")


def redact_string(value: str) -> str:
    value = _BEARER.sub("Bearer [REDACTED]", value)
    value = _EMAIL.sub("[REDACTED_EMAIL]", value)
    value = _PHONE_BD.sub("[REDACTED_PHONE]", value)
    value = _CARDISH.sub("[REDACTED_NUMBER]", value)
    return value


def redact_value(value: Any) -> Any:
    if isinstance(value, str):
        return redact_string(value)
    if isinstance(value, dict):
        return {k: redact_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_value(v) for v in value]
    if isinstance(value, tuple):
        return tuple(redact_value(v) for v in value)
    return value


def redaction_processor(
    _logger: object,
    _method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    result = redact_value(event_dict)
    assert isinstance(result, dict)
    return result
