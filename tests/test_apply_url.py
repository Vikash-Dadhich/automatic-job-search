"""Tests for apply-URL classification (LinkedIn → company Workday)."""

from __future__ import annotations

from core.apply_url import (
    ApplyKind,
    classify_apply_url,
    is_automateable_apply_url,
    is_workday_url,
    workday_parts,
)
from core.db import Source
from scraper.models import RawPosting, to_job


def test_classify_workday() -> None:
    url = "https://meijer.wd5.myworkdayjobs.com/Meijer/job/City/Title_R1"
    assert classify_apply_url(url) == ApplyKind.workday
    assert is_workday_url(url)
    assert is_automateable_apply_url(url)
    parts = workday_parts(url)
    assert parts is not None
    assert parts.tenant == "meijer"


def test_classify_linkedin_listing() -> None:
    url = "https://www.linkedin.com/jobs/view/123"
    assert classify_apply_url(url) == ApplyKind.linkedin
    assert not is_automateable_apply_url(url)


def test_classify_company_site() -> None:
    url = "https://www.amazon.jobs/en/jobs/123"
    assert classify_apply_url(url) == ApplyKind.company
    assert not is_automateable_apply_url(url)


def test_classify_ziprecruiter_and_google() -> None:
    zip_url = "https://www.ziprecruiter.com/jobs/acme/product-manager-intern"
    assert classify_apply_url(zip_url) == ApplyKind.zip_recruiter
    assert not is_automateable_apply_url(zip_url)

    google_url = "https://www.google.com/search?q=jobs#htivrt=jobs"
    assert classify_apply_url(google_url) == ApplyKind.google
    assert not is_automateable_apply_url(google_url)


def test_to_job_stamps_workday_tenant_from_linkedin_url() -> None:
    posting = RawPosting(
        source=Source.linkedin,
        external_id="li-99",
        title="PM",
        company="HP",
        url=(
            "https://hp.wd5.myworkdayjobs.com/en-US/ExternalCareerSite/job/"
            "Tustin/Title_R1"
        ),
    )
    job = to_job(posting)
    assert job.source == Source.linkedin
    assert job.tenant == "hp"
