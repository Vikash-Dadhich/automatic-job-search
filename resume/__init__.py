"""Resume preparation: static base PDF by default, Typst tailoring on demand."""

from resume.baseline import build_role_baseline
from resume.compiler import (
    FitReport,
    ResumeSummary,
    clean_name,
    compile_for_job,
    compile_pending,
    compile_resume,
    compile_resume_data,
    prepare_base_resume,
    prepare_pending,
    sanitize_pdf,
)
from resume.diff import generate_suggestions_for_job
from resume.selector import build_resume_data, select_bullets
from resume.skills import aggregate_role_skills, extract_top_skills

__all__ = [
    "FitReport",
    "ResumeSummary",
    "aggregate_role_skills",
    "build_resume_data",
    "build_role_baseline",
    "clean_name",
    "compile_for_job",
    "compile_pending",
    "compile_resume",
    "compile_resume_data",
    "extract_top_skills",
    "generate_suggestions_for_job",
    "prepare_base_resume",
    "prepare_pending",
    "sanitize_pdf",
    "select_bullets",
]
