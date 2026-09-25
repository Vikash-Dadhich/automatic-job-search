"""Tests for Workday URL parsing and targets loading."""

from __future__ import annotations

import pytest

from config.targets import SearchConfig, WorkdayTenant, load_targets, parse_workday_url


def test_parse_nvidia_careers_url() -> None:
    parts = parse_workday_url(
        "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite"
    )
    assert parts.tenant == "nvidia"
    assert parts.shard == "wd5"
    assert parts.site == "NVIDIAExternalCareerSite"
    assert parts.host == "nvidia.wd5.myworkdayjobs.com"
    assert parts.base_cxs.endswith("/wday/cxs/nvidia/NVIDIAExternalCareerSite")


def test_parse_locale_deep_link() -> None:
    parts = parse_workday_url(
        "https://acme.wd3.myworkdayjobs.com/fr-CA/External_Career_Site/job/Montreal/Dev_JR1"
    )
    assert parts.tenant == "acme"
    assert parts.shard == "wd3"
    assert parts.site == "External_Career_Site"


def test_parse_cxs_api_path() -> None:
    parts = parse_workday_url(
        "https://salesforce.wd12.myworkdayjobs.com/wday/cxs/salesforce/External_Career_Site/jobs"
    )
    assert parts.tenant == "salesforce"
    assert parts.shard == "wd12"
    assert parts.site == "External_Career_Site"


def test_parse_invalid_host() -> None:
    with pytest.raises(ValueError, match="Workday careers host"):
        parse_workday_url("https://example.com/careers")


def test_placeholder_tenant_skipped() -> None:
    tenant = WorkdayTenant(
        name="PLACEHOLDER_COMPANY",
        url="https://placeholder.wd1.myworkdayjobs.com/External",
    )
    assert tenant.is_placeholder is True


def test_load_targets_defaults() -> None:
    load_targets.cache_clear()
    targets = load_targets()
    assert targets.search.hours_old == 36
    assert "linkedin" in targets.search.sites
    assert targets.active_workday_tenants() == []


def test_search_config_accepts_all_supported_sites() -> None:
    cfg = SearchConfig(
        terms=["Product Manager Intern"],
        sites=["linkedin", "indeed", "google", "zip_recruiter"],
    )
    assert cfg.sites == ["linkedin", "indeed", "google", "zip_recruiter"]


def test_search_config_rejects_unknown_site() -> None:
    with pytest.raises(ValueError, match="Unsupported sites"):
        SearchConfig(terms=["x"], sites=["monster"])
