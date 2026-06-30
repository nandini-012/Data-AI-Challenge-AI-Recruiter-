import re

from app.services.skill_extractor import (
    CAREER_EVIDENCE_GROUPS,
    extract_jd_keywords,
    is_relevant_skill,
    normalize_skill_name,
)

RELEVANT_SKILLS, PRODUCTION_TERMS, STRONG_TITLES, MEDIUM_TITLES = extract_jd_keywords()

_CAREER_TEXT_CLEAN_RE = re.compile(r"[^a-z0-9+#.]+")
_CAREER_BOUNDARY_TEXT_RE = re.compile(r"[^a-z0-9]+")

CAREER_EVIDENCE_PATTERNS = {
    group: [
        re.compile(r"(?<![a-z0-9])" + re.escape(term.lower()) + r"(?![a-z0-9])")
        for term in terms
    ]
    for group, terms in CAREER_EVIDENCE_GROUPS.items()
}

CAREER_EVIDENCE_GROUP_TERMS = {
    group: tuple(term.lower() for term in terms)
    for group, terms in CAREER_EVIDENCE_GROUPS.items()
}

ALL_CAREER_EVIDENCE_PATTERNS = [
    pattern
    for patterns in CAREER_EVIDENCE_PATTERNS.values()
    for pattern in patterns
]

ALL_CAREER_EVIDENCE_TERMS = tuple(
    term.lower()
    for terms in CAREER_EVIDENCE_GROUPS.values()
    for term in terms
)

CAREER_EVIDENCE_WEIGHTS = {
    "build": 0.16,
    "deployment": 0.25,
    "scale": 0.16,
    "operations": 0.18,
    "data_pipeline": 0.16,
    "ai_systems": 0.24,
}


JUNIOR_TITLE_TERMS = ("junior", "jr", "associate")


def has_junior_or_associate_title(title: str) -> bool:
    title_l = (title or "").lower()
    return any(
        re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", title_l)
        for term in JUNIOR_TITLE_TERMS
    )


def has_title_experience_inconsistency(title: str, years: float) -> bool:
    return has_junior_or_associate_title(title) and (years or 0) > 5


def title_relevance_score(title: str, years: float = 0) -> float:
    title_l = (title or "").lower()
    if any(k in title_l for k in STRONG_TITLES):
        score = 1.0
    elif any(k in title_l for k in MEDIUM_TITLES):
        score = 0.7
    else:
        score = 0.2

    if has_junior_or_associate_title(title):
        score *= 0.85

    return round(score, 3)


def skill_match_score(skills: list) -> float:
    """
    Weighted by duration_months + endorsements using normalized exact skills.
    Keeps aliases useful while preventing duplicate keyword-stuffing.
    """
    best_scores_by_skill = {}
    for s in skills:
        skill_name = s.get("name") or ""
        canonical_name = normalize_skill_name(skill_name)
        if is_relevant_skill(skill_name):
            duration_weight = min((s.get("duration_months", 0) or 0) / 24, 1.0)
            endorsement_boost = min((s.get("endorsements", 0) or 0) / 20, 0.3)
            skill_score = duration_weight + endorsement_boost
            best_scores_by_skill[canonical_name] = max(
                best_scores_by_skill.get(canonical_name, 0),
                skill_score,
            )

    score = sum(best_scores_by_skill.values())
    return min(score / 6, 1.0)


def _has_evidence(text: str, pattern) -> bool:
    return pattern.search(text) is not None


def _clean_career_text(value: str) -> str:
    return _CAREER_TEXT_CLEAN_RE.sub(" ", (value or "").lower())


def _career_match_text(value: str) -> str:
    return " " + _CAREER_BOUNDARY_TEXT_RE.sub(" ", value) + " "


def _has_career_term(text: str, terms: tuple) -> bool:
    return any(f" {term} " in text for term in terms)


def career_substance_score(career_history: list) -> float:
    """
    Scores diverse engineering evidence, not repeated keyword occurrences.
    """
    job_texts = [
        _clean_career_text(job.get("description", ""))
        for job in career_history
    ]
    job_match_texts = [_career_match_text(job_text) for job_text in job_texts]
    text = " ".join(job_match_texts)

    matched_groups = {
        group
        for group, terms in CAREER_EVIDENCE_GROUP_TERMS.items()
        if _has_career_term(text, terms)
    }

    score = sum(CAREER_EVIDENCE_WEIGHTS[group] for group in matched_groups)

    # Small quality bonus when evidence appears across multiple roles.
    jobs_with_evidence = 0
    for job_text in job_match_texts:
        if _has_career_term(job_text, ALL_CAREER_EVIDENCE_TERMS):
            jobs_with_evidence += 1

    score += min(jobs_with_evidence, 3) * 0.03
    return min(score, 1.0)


def experience_fit_score(years: float) -> float:
    """JD targets 5-9 years."""
    if 5 <= years <= 9:
        return 1.0
    elif 3 <= years < 5 or 9 < years <= 12:
        return 0.6
    else:
        return 0.3


def behavioral_multiplier(signals: dict, days_since_active: int) -> float:
    """Used as multiplier on base score — not additive."""
    mult = 1.0
    if days_since_active > 180:
        mult *= 0.6
    elif days_since_active > 90:
        mult *= 0.85
    mult *= (0.7 + 0.5 * (signals.get("recruiter_response_rate") or 0))
    if signals.get("interview_completion_rate", 1) < 0.5:
        mult *= 0.9
    if signals.get("open_to_work_flag"):
        mult *= 1.05
    return round(mult, 3)
