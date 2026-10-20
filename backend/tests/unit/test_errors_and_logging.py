from __future__ import annotations

from app.core.errors.envelope import ErrorEnvelope
from app.core.errors.exceptions import NotFoundError
from app.core.logging.context import trace_id_var
from app.core.logging.redaction import redact_string


def test_error_envelope_shape() -> None:
    body = ErrorEnvelope.model_validate(
        {
            "error": {
                "code": "common.not_found",
                "message": "missing",
                "details": {},
                "trace_id": "abc",
            },
        },
    )
    assert body.error.code == "common.not_found"


def test_redaction_masks_email_and_phone() -> None:
    raw = "contact user@example.com or 01712345678"
    redacted = redact_string(raw)
    assert "user@example.com" not in redacted
    assert "01712345678" not in redacted


def test_logs_include_trace_id() -> None:
    from app.core.logging.setup import _add_contextvars

    trace_id_var.set("trace-123")
    event_dict: dict[str, object] = {"event": "hello"}
    enriched = _add_contextvars(None, "info", event_dict)
    assert enriched.get("trace_id") == "trace-123"


def test_not_found_error_code() -> None:
    err = NotFoundError("item missing")
    assert err.http_status == 404
    assert err.code == "common.not_found"
