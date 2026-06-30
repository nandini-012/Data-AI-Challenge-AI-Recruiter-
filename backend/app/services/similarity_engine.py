import re
from functools import lru_cache

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

@lru_cache(maxsize=8192)
def _clean_term(value: str) -> str:
    return re.sub(r"[^a-z0-9+#.]+", " ", (value or "").lower()).strip()


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


def title_relevance_score_jd(title: str, years: float = 0, jd_context=None) -> float:
    """Score title relevance against the supplied JD context."""
    if jd_context is None:
        return title_relevance_score(title, years)

    title_l = f" {_clean_term(title)} "
    strong = jd_context.get("_strong_title_terms")
    if strong is None:
        strong = tuple(_clean_term(term) for term in jd_context.get("strong_titles", ()))
        jd_context["_strong_title_terms"] = strong
    medium = jd_context.get("_medium_title_terms")
    if medium is None:
        medium = tuple(_clean_term(term) for term in jd_context.get("medium_titles", ()))
        jd_context["_medium_title_terms"] = medium

    if strong and any(f" {term} " in title_l for term in strong if term):
        score = 1.0
    elif medium and any(f" {term} " in title_l for term in medium if term):
        score = 0.65
    else:
        role_tokens = {
            token
            for term in strong + medium
            for token in term.split()
            if len(token) > 3
        }
        score = 0.25 if any(f" {token} " in title_l for token in role_tokens) else 0.05

    if has_junior_or_associate_title(title):
        score *= 0.85

    return round(score, 3)


def _jd_skill_terms(jd_context) -> set:
    cached = jd_context.get("_skill_term_set")
    if cached is not None:
        return cached

    terms = set()
    for skill in jd_context.get("relevant_skills", ()):
        terms.add(_clean_term(skill))
        terms.add(_clean_term(normalize_skill_name(skill)))
    terms.update(jd_context.get("skill_terms", ()))
    terms = {term for term in terms if term}
    jd_context["_skill_term_set"] = terms
    return terms


def _skill_match_name(skill_name: str, jd_terms: set):
    if not jd_terms:
        return None
    canonical = normalize_skill_name(skill_name)
    if _clean_term(skill_name) in jd_terms or _clean_term(canonical) in jd_terms:
        return canonical
    return None


def score_and_match_skills_jd(skills, jd_context=None):
    if jd_context is None:
        best_scores = {}
        matched = []
        seen = set()
        for skill in skills or []:
            skill_name = skill.get("name") or ""
            if not is_relevant_skill(skill_name):
                continue
            canonical = normalize_skill_name(skill_name)
            duration_weight = min((skill.get("duration_months", 0) or 0) / 24, 1.0)
            endorsement_boost = min((skill.get("endorsements", 0) or 0) / 20, 0.3)
            best_scores[canonical] = max(best_scores.get(canonical, 0), duration_weight + endorsement_boost)
            if canonical not in seen:
                seen.add(canonical)
                matched.append(canonical)
        return min(sum(best_scores.values()) / 6, 1.0), matched

    jd_terms = _jd_skill_terms(jd_context)
    if not jd_terms:
        return 0.0, []

    best_scores = {}
    matched = []
    seen = set()
    for skill in skills or []:
        canonical = _skill_match_name(skill.get("name") or "", jd_terms)
        if not canonical:
            continue
        duration_weight = min((skill.get("duration_months", 0) or 0) / 24, 1.0)
        endorsement_boost = min((skill.get("endorsements", 0) or 0) / 20, 0.3)
        best_scores[canonical] = max(
            best_scores.get(canonical, 0),
            duration_weight + endorsement_boost,
        )
        if canonical not in seen:
            seen.add(canonical)
            matched.append(canonical)

    denominator = max(1, min(len(jd_context.get("relevant_skills", ())) or len(jd_terms), 6))
    return min(sum(best_scores.values()) / denominator, 1.0), matched


def matched_candidate_skills_jd(skills, jd_context=None) -> list:
    _, matched = score_and_match_skills_jd(skills, jd_context)
    return matched


def skill_match_score_jd(skills, jd_context=None):
    score, _ = score_and_match_skills_jd(skills, jd_context)
    return score


def career_substance_score_jd(career_history: list, jd_context=None) -> float:
    if jd_context is None:
        return career_substance_score(career_history)

    career_tokens = jd_context.get("career_term_tokens")
    if career_tokens is None:
        career_tokens = tuple(
            f" {term} "
            for term in jd_context.get("career_terms", ())
            if term
        )
        jd_context["career_term_tokens"] = career_tokens
    if not career_tokens:
        return 0.0

    job_texts = [
        _career_match_text(_clean_career_text(job.get("description", "")))
        for job in career_history or []
    ]
    all_text = " ".join(job_texts)
    matched_terms = {
        term_token
        for term_token in career_tokens
        if term_token in all_text
    }
    if not matched_terms:
        return 0.0

    coverage_denominator = max(1, min(len(career_tokens), 8))
    coverage_score = min(len(matched_terms) / coverage_denominator, 1.0) * 0.76
    jobs_with_evidence = sum(
        1
        for job_text in job_texts
        if any(term_token in job_text for term_token in career_tokens)
    )
    role_depth_score = min(jobs_with_evidence, 3) * 0.08
    return min(coverage_score + role_depth_score, 1.0)


def experience_fit_score_jd(years: float, jd_context=None) -> float:
    """Score experience fit against the supplied JD context's experience band."""
    if jd_context is None:
        return experience_fit_score(years)

    exp_min = jd_context.get("exp_min", 5)
    exp_max = jd_context.get("exp_max", 9)

    if exp_min <= years <= exp_max:
        return 1.0
    elif (exp_min - 2) <= years < exp_min or exp_max < years <= (exp_max + 3):
        return 0.6
    else:
        return 0.3
