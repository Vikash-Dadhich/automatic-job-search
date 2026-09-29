"""Phase 7 portfolio weights. They do not change fit, tier, status, or search capacity."""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from core.db import Job, Source, Status, Tier, session_scope, upsert_job
from scorer.engine import compute_tier
from scorer.prerank import prerank_score
from scorer.role_classify import PRIMARY_FAMILIES, SUBFAMILY_FAMILY
from scorer.role_weights import (
    ROLE_WEIGHT_VERSION,
    get_role_family_weight,
    load_role_family_weights,
    weight_for_subfamily,
)
from scraper.discovery import load_discovery
from scraper.models import RawPosting, to_job

EXPECTED = {
    "PRODUCT_MANAGEMENT": 40,
    "CONSULTING": 40,
    "STRATEGY_TRANSFORMATION": 15,
    "PRODUCT_MARKETING": 5,
    "PROGRAM_PROJECT_OPERATIONS": 5,
    "MARKETING": 5,
    "OTHER": 5,
    "UNKNOWN": 5,
}


@pytest.mark.parametrize(("family", "weight"), list(EXPECTED.items()))
def test_primary_family_weights(family: str, weight: int) -> None:
    assert get_role_family_weight(family) == weight


def test_missing_role_family_uses_unknown_weight() -> None:
    assert get_role_family_weight(None) == 5


def test_unrecognized_role_family_uses_unknown_weight() -> None:
    assert get_role_family_weight("NOT_A_FAMILY") == 5
    assert get_role_family_weight("pm_core") == 5


def test_every_phase5_primary_family_has_a_weight() -> None:
    loaded = load_role_family_weights()
    assert set(loaded) == set(PRIMARY_FAMILIES)
    for family in PRIMARY_FAMILIES:
        assert get_role_family_weight(family) == EXPECTED[family]


def test_subfamilies_inherit_the_primary_family_weight() -> None:
    assert SUBFAMILY_FAMILY
    for subfamily, family in SUBFAMILY_FAMILY.items():
        assert weight_for_subfamily(subfamily) == EXPECTED[family]
        assert get_role_family_weight(subfamily) == EXPECTED["UNKNOWN"]


def test_seven_weights_are_not_required_to_sum_to_100() -> None:
    loaded = load_role_family_weights()
    assert sum(loaded.values()) == 120


def test_discovery_capacity_stays_independent() -> None:
    families = {family.id: family.weight for family in load_discovery().families}
    assert families["PRODUCT_MANAGEMENT"] == Decimal("0.40")
    assert families["CONSULTING"] == Decimal("0.40")
    assert families["STRATEGY_TRANSFORMATION"] == Decimal("0.15")
    assert families["OTHER"] == Decimal("0.05")
    assert get_role_family_weight("STRATEGY_TRANSFORMATION") == 15


def test_discovery_labels_do_not_choose_the_weight() -> None:
    assert get_role_family_weight("STRATEGY_TRANSFORMATION") == 15


def test_company_and_vector_are_not_weight_inputs() -> None:
    assert get_role_family_weight("CONSULTING") == 40


def _posting(external_id: str, **kwargs: object) -> RawPosting:
    defaults: dict[str, object] = {
        "source": Source.linkedin,
        "external_id": external_id,
        "title": "Product Manager Intern",
        "company": "Acme",
        "location": "Seattle, WA",
        "url": f"https://example.com/jobs/{external_id}",
        "description_clean": "Requirements\nOwn the roadmap for an internship team. " * 4,
    }
    defaults.update(kwargs)
    return RawPosting(**defaults)  # type: ignore[arg-type]


def _job(
    external_id: str,
    *,
    role_family: str | None,
    score: int = 80,
    company: str = "Acme",
    discovery_family: str | None = "OTHER",
    discovery_bucket: str | None = "OTHER",
    discovery_query: str | None = "some query",
    source: Source = Source.linkedin,
    vector_score: float | None = 0.2,
) -> Job:
    job = to_job(
        _posting(external_id, company=company, source=source),
        status=Status.staged,
    )
    job.score = score
    job.tier = Tier.one
    job.role_family = role_family
    job.role_family_weight = 99
    job.discovery_family = discovery_family
    job.discovery_bucket = discovery_bucket
    job.discovery_query = discovery_query
    job.vector_score = vector_score
    return job


async def test_same_fit_keeps_separate_portfolio_weights(db_ready: Path, profile) -> None:
    specs = [
        ("a", "PRODUCT_MANAGEMENT", 40),
        ("b", "CONSULTING", 40),
        ("c", "STRATEGY_TRANSFORMATION", 15),
        ("d", "PRODUCT_MARKETING", 5),
    ]
    async with session_scope() as session:
        saved = []
        for external_id, family, _weight in specs:
            saved.append(await upsert_job(session, _job(external_id, role_family=family)))
        for job, (_external_id, family, weight) in zip(saved, specs, strict=True):
            assert job.score == 80
            assert job.role_family == family
            assert job.role_family_weight == weight
            assert job.role_family_weight_version == ROLE_WEIGHT_VERSION
            assert job.tier == Tier.one
            assert job.status == Status.staged
            assert compute_tier(80, job.company, profile) == Tier.two
        for external_id, family, weight in (
            ("a90", "PRODUCT_MANAGEMENT", 40),
            ("b90", "CONSULTING", 40),
            ("c90", "STRATEGY_TRANSFORMATION", 15),
            ("d90", "PRODUCT_MARKETING", 5),
        ):
            job = await upsert_job(session, _job(external_id, role_family=family, score=90))
            assert job.score == 90
            assert job.role_family_weight == weight
            assert compute_tier(90, job.company, profile) == Tier.one


async def test_provenance_and_company_do_not_change_weight(db_ready: Path) -> None:
    async with session_scope() as session:
        first = await upsert_job(
            session,
            _job(
                "same-role",
                role_family="PRODUCT_MANAGEMENT",
                company="Google",
                discovery_family="CONSULTING",
                discovery_bucket="STRATEGY_CONSULTING",
                discovery_query="management consultant intern",
                source=Source.indeed,
                vector_score=0.11,
            ),
        )
        second = await upsert_job(
            session,
            _job(
                "same-role",
                role_family="PRODUCT_MANAGEMENT",
                company="Unknown Startup",
                discovery_family="PRODUCT_MARKETING",
                discovery_bucket="PRODUCT_MARKETING",
                discovery_query="product marketing intern",
                source=Source.linkedin,
                vector_score=0.94,
            ),
        )
    assert first.role_family_weight == 40
    assert second.role_family_weight == 40
    assert second.score == 80
    assert second.tier == Tier.one
    assert second.status == Status.staged
    assert second.company == "Unknown Startup"
    assert second.discovery_query == "product marketing intern"


def test_prerank_ignores_role_family_weight(profile) -> None:
    left = _job("left", role_family="PRODUCT_MANAGEMENT")
    right = _job("right", role_family="PRODUCT_MARKETING")
    left.role_family_weight = 40
    right.role_family_weight = 5
    assert prerank_score(left, profile) == prerank_score(right, profile)


def test_tier_function_ignores_role_family_weight(profile) -> None:
    assert compute_tier(90, "Acme", profile) == Tier.one
    assert compute_tier(80, "Acme", profile) == Tier.two
    for family, weight in EXPECTED.items():
        assert get_role_family_weight(family) == weight


def _write_weights(path: Path, weights: Mapping[str, object]) -> None:
    path.write_text(
        yaml.safe_dump({"version": ROLE_WEIGHT_VERSION, "weights": weights}),
        encoding="utf-8",
    )


def test_malformed_weight_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "weights.yaml"
    _write_weights(path, {**EXPECTED, "PRODUCT_MANAGEMENT": 101})
    with pytest.raises(ValueError, match="0 through 100"):
        load_role_family_weights(str(path))

    _write_weights(path, {**EXPECTED, "CONSULTING": "40"})
    with pytest.raises(ValueError, match="integer"):
        load_role_family_weights(str(path))

    _write_weights(path, {**EXPECTED, "OTHER": True})
    with pytest.raises(ValueError, match="integer"):
        load_role_family_weights(str(path))


def test_missing_or_extra_family_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "weights.yaml"
    incomplete = dict(EXPECTED)
    del incomplete["UNKNOWN"]
    _write_weights(path, incomplete)
    with pytest.raises(ValueError, match="missing"):
        load_role_family_weights(str(path))

    extra = {**EXPECTED, "PM_CORE": 40}
    _write_weights(path, extra)
    with pytest.raises(ValueError, match="extra"):
        load_role_family_weights(str(path))
