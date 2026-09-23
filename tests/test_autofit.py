"""Tests for one-page auto-fit resume compilation."""

from __future__ import annotations

from pathlib import Path

from resume.compiler import (
    FitReport,
    apply_fit_caps,
    compile_resume_data,
    pdf_page_count,
)


def _base_data(**overrides) -> dict:
    data = {
        "name": "Jane Q. Doe",
        "email": "jane@example.com",
        "phone": "+1-555-111-2222",
        "location": "Seattle, WA",
        "linkedin": "https://www.linkedin.com/in/janedoe",
        "github": "https://github.com/janedoe",
        "portfolio": "",
        "summary": "Software engineer targeting backend roles.",
        "skills": ["Python", "SQL", "Kubernetes", "FastAPI", "React"],
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Acme",
                "location": "Seattle, WA",
                "start": "2022-01",
                "end": "2024-01",
                "bullets": [
                    "Built Python APIs with FastAPI serving 1M requests/day.",
                    "Designed SQL data models and optimized Postgres queries.",
                    "Deployed Kubernetes services with Helm and CI/CD.",
                    "Led stakeholder demos and wrote design docs.",
                ],
            }
        ],
        "education": [
            {
                "degree": "M.S.",
                "field": "Computer Science",
                "school": "Example University",
                "location": "Seattle, WA",
                "graduation": "2024-05",
                "gpa": 3.8,
            }
        ],
    }
    data.update(overrides)
    return data


def test_apply_fit_caps_trims_skills_and_bullets() -> None:
    data = _base_data()
    capped = apply_fit_caps(
        data,
        max_bullets=2,
        skills_cap=2,
        font_size=10,
        leading=0.65,
        section_gap=0.55,
    )
    assert len(capped["skills"]) == 2
    total_bullets = sum(len(e["bullets"]) for e in capped["experience"])
    assert total_bullets == 2
    assert capped["font_size"] == 10


def test_compile_small_resume_one_page(tmp_path: Path) -> None:
    out = tmp_path / "small.pdf"
    fit = compile_resume_data(_base_data(), out, autofit=True)
    assert out.is_file()
    assert pdf_page_count(out) == 1
    assert fit.pages == 1
    assert isinstance(fit, FitReport)


def test_compile_oversized_autofits_to_one_page(tmp_path: Path) -> None:
    long_bullet = (
        "Delivered cross-functional initiatives spanning product strategy, "
        "engineering execution, stakeholder alignment, go-to-market planning, "
        "and post-launch analytics across multiple business units with measurable "
        "revenue impact and operational efficiency gains. "
    ) * 3
    experience = []
    for i in range(6):
        experience.append(
            {
                "title": f"Engineer {i}",
                "company": f"Company {i}",
                "location": "Seattle, WA",
                "start": "2020-01",
                "end": "2021-01",
                "bullets": [f"{long_bullet} item {j}" for j in range(8)],
            }
        )
    skills = [f"Skill-{i}" for i in range(60)]
    data = _base_data(
        summary=long_bullet,
        skills=skills,
        experience=experience,
    )
    out = tmp_path / "big.pdf"
    fit = compile_resume_data(data, out, autofit=True)
    assert out.is_file()
    assert fit.pages == 1
    assert pdf_page_count(out) == 1
    assert fit.attempts >= 1
