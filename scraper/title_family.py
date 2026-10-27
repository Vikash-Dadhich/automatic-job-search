"""Which kind of role a job title is, read from the title alone.

The owner judges a card by its title, so the queue mix (product, consulting,
other business roles) is decided by the same words he sees. This is a cheap,
deterministic reading. It does not score fit and never calls a model.
"""

from __future__ import annotations

import re

PRODUCT = "PRODUCT_MANAGEMENT"
CONSULTING = "CONSULTING"
STRATEGY = "STRATEGY_TRANSFORMATION"
PRODUCT_MARKETING = "PRODUCT_MARKETING"
MARKETING = "MARKETING"
OPERATIONS = "PROGRAM_PROJECT_OPERATIONS"
GENERAL_MBA = "GENERAL_MBA"

TARGET_FAMILIES = (
    PRODUCT,
    CONSULTING,
    STRATEGY,
    PRODUCT_MARKETING,
    MARKETING,
    OPERATIONS,
    GENERAL_MBA,
)

# A title that is plainly a technical, research, design or support job is not a
# target, even when it also says "product" (for example "Software Engineer, Product").
_NOT_TARGET = re.compile(
    r"\bengineer|\bengineering intern|\bdeveloper\b|\bsoftware\b(?!.*\bproduct manag)|"
    r"\bscientist\b|\bdata scien|\bresearch(er)?\b|\bph\.?d\b|\bdesigner\b|\bux\b|\bui\b|"
    r"\bmachine learning engineer|\btechnician\b|\bmechanic|\bnurs|\bclinical\b|\bpharmac|"
    r"\baccount(ant|ing)\b|\baudit\b|\btax\b|\blegal\b|\bparalegal|\bcounsel\b|\brecruit|"
    r"\bteller\b|\bcashier\b|\bwarehouse\b|\bdriver\b|\btrainer\b|\btechnical support\b|"
    r"\bhelp ?desk\b|\bcustomer (service|support)\b|\bsales (representative|associate)\b|"
    r"\bteaching\b|\btutor\b|\bdata analyst\b|\bdata engineer|\bactuar",
    re.IGNORECASE,
)

_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    (PRODUCT_MARKETING, re.compile(r"\bproduct marketing\b|\bpmm\b", re.IGNORECASE)),
    (
        PRODUCT,
        re.compile(
            r"\bproduct manag|\bproduct owner\b|\bapm\b|\bassociate product\b|"
            r"\bproduct (lead|strategy|management|operations|ops|intern|internship|"
            r"development|innovation|growth)\b|\bproduct\b.*\b(mba|summer associate)\b|"
            r"\b(mba|summer associate)\b.*\bproduct\b",
            re.IGNORECASE,
        ),
    ),
    (
        CONSULTING,
        re.compile(r"\bconsult|\badvisory\b|\bdeal advisory\b", re.IGNORECASE),
    ),
    (
        STRATEGY,
        re.compile(
            r"\bstrateg|\bcorporate development\b|\bcorp ?dev\b|\btransformation\b|"
            r"\bchief of staff\b|\bbiz ?ops\b|\bbusiness operations\b|\bgeneral management\b|"
            r"\bfounder'?s office\b|\bventure\b|\binnovation\b",
            re.IGNORECASE,
        ),
    ),
    (
        MARKETING,
        re.compile(
            r"\bmarketing\b|\bbrand\b|\bgo[- ]to[- ]market\b|\bgtm\b|\bgrowth\b",
            re.IGNORECASE,
        ),
    ),
    (
        OPERATIONS,
        re.compile(
            r"\bprogram manag|\bproject manag|\boperations\b|\bbusiness analyst\b|"
            r"\bpartnerships?\b|\bbusiness development\b",
            re.IGNORECASE,
        ),
    ),
    (
        GENERAL_MBA,
        re.compile(r"\bmba\b|\bsummer associate\b|\bleadership development\b", re.IGNORECASE),
    ),
)

# Words that make a business reading certain, so they win over a broad exclusion
# like "software" in "Software Product Manager Intern".
_STRONG = re.compile(r"\bproduct manag|\bproduct owner\b|\bconsult|\bstrateg", re.IGNORECASE)
# These always mean the role is not one of his targets.
_HARD_NOT_TARGET = re.compile(
    r"\bengineer|\bdeveloper\b|\bscientist\b|\bph\.?d\b|\bdesigner\b", re.IGNORECASE
)


def title_family(title: str | None) -> str | None:
    """The target family a title belongs to, or None when it is not a target role."""
    text = (title or "").strip()
    if not text:
        return None
    if _HARD_NOT_TARGET.search(text):
        return None
    if _NOT_TARGET.search(text) and not _STRONG.search(text):
        return None
    for family, pattern in _RULES:
        if pattern.search(text):
            return family
    return None


def is_target_title(title: str | None) -> bool:
    return title_family(title) is not None
