"""Strategic weight of a classified role family. Not fit and not search capacity."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from scorer.role_classify import PRIMARY_FAMILIES, SUBFAMILY_FAMILY

WEIGHTS_PATH = Path(__file__).resolve().parent.parent / "config" / "role_family_weights.yaml"
ROLE_WEIGHT_VERSION = "phase7-v1"


def _validate(raw: object) -> dict[str, int]:
    if not isinstance(raw, dict):
        raise ValueError("role-family weights must be a mapping")
    version = raw.get("version")
    if version != ROLE_WEIGHT_VERSION:
        raise ValueError(f"role-family weight version must be {ROLE_WEIGHT_VERSION}")
    weights = raw.get("weights")
    if not isinstance(weights, dict):
        raise ValueError("role-family weights.weights must be a mapping")
    keys = set(weights)
    if keys != set(PRIMARY_FAMILIES):
        missing = sorted(set(PRIMARY_FAMILIES) - keys)
        extra = sorted(keys - set(PRIMARY_FAMILIES))
        raise ValueError(
            "role-family weights must match Phase 5 families; "
            f"missing={missing} extra={extra}"
        )
    parsed: dict[str, int] = {}
    for name, value in weights.items():
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"weight for {name} must be an integer from 0 through 100")
        if value < 0 or value > 100:
            raise ValueError(f"weight for {name} must be an integer from 0 through 100")
        parsed[str(name)] = value
    return parsed


@lru_cache
def load_role_family_weights(path: str | None = None) -> dict[str, int]:
    """Load the portfolio weights. Raises if the file does not match Phase 5 families."""
    target = Path(path) if path else WEIGHTS_PATH
    with target.open(encoding="utf-8") as handle:
        raw: Any = yaml.safe_load(handle)
    return _validate(raw)


def get_role_family_weight(role_family: str | None) -> int:
    """Portfolio weight for a Phase 5 primary family. Missing or unknown names use UNKNOWN."""
    weights = load_role_family_weights()
    if role_family is None:
        return weights["UNKNOWN"]
    return weights.get(role_family, weights["UNKNOWN"])


def weight_for_subfamily(subfamily: str | None) -> int:
    """Subfamilies use their primary family's weight. They do not have their own."""
    if not subfamily:
        return get_role_family_weight(None)
    return get_role_family_weight(SUBFAMILY_FAMILY.get(subfamily))
