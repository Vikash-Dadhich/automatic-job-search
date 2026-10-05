"""Short error text for logs and run evidence. Secrets do not survive."""

from __future__ import annotations

import re

_ERROR_LIMIT = 200

_BEARER = re.compile(r"(?i)(bearer\s+)\S+")
_BASIC = re.compile(r"(?i)(authorization\s*:\s*basic\s+)\S+")
_SK_TOKEN = re.compile(r"(?i)\bsk-[A-Za-z0-9_-]{8,}")
_ASSIGNED = re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|token|password|secret|authorization)"
    r"(\s*[=:]\s*)(?!basic\b)\S+"
)
_DATABASE_USERINFO = re.compile(r"(?i)((?:postgres|sqlite)(?:ql)?(?:\+\w+)?://)[^@\s/]+@")
_QUERY_SECRET = re.compile(
    r"(?i)([?&](?:token|key|sig|auth|password|access_token|api_key)=)[^&\s]+"
)


def redact_error(text: str, *, limit: int = _ERROR_LIMIT) -> str:
    """Drop credential-shaped text, then keep a single short line.

    Covered patterns: bearer tokens, unlabeled ``sk-`` tokens, assigned
    secrets, ``Authorization: Basic`` values, database userinfo, and
    ``token``/``key``/``sig``/``auth``/``password`` query parameters.
    Other secret shapes can still remain.
    """
    cleaned = text.replace("\n", " ").replace("\r", " ")
    cleaned = _BEARER.sub(r"\1[redacted]", cleaned)
    cleaned = _BASIC.sub(r"\1[redacted]", cleaned)
    cleaned = _SK_TOKEN.sub("[redacted]", cleaned)
    cleaned = _ASSIGNED.sub(r"\1\2[redacted]", cleaned)
    cleaned = _DATABASE_USERINFO.sub(r"\1[redacted]@", cleaned)
    cleaned = _QUERY_SECRET.sub(r"\1[redacted]", cleaned)
    return cleaned[:limit]
