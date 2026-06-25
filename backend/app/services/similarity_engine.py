from app.services.skill_extractor import extract_jd_keywords

RELEVANT_SKILLS, PRODUCTION_TERMS, STRONG_TITLES, MEDIUM_TITLES = extract_jd_keywords()


def title_relevance_score(title: str) -> float:
    title_l = (title or "").lower()
    if any(k in title_l for k in STRONG_TITLES):
        return 1.0
    if any(k in title_l for k in MEDIUM_TITLES):
        return 0.7
    return 0.2


def skill_match_score(skills: list) -> float:
    """
    Weighted by duration_months + endorsements.
    Kills keyword-stuffer profiles.
    """
    score = 0
    for s in skills:
        name_l = (s.get("name") or "").lower()
        if any(r in name_l for r in RELEVANT_SKILLS):
            weight = min((s.get("duration_months", 0) or 0) / 24, 1.0)
            endorsement_boost = min((s.get("endorsements", 0) or 0) / 20, 0.3)
            score += weight + endorsement_boost
    return min(score / 6, 1.0)


def career_substance_score(career_history: list) -> float:
    """
    Looks for production/deployment language in career descriptions.
    """
    text = " ".join(
        j.get("description", "") for j in career_history
    ).lower()
    hits = sum(1 for t in PRODUCTION_TERMS if t in text)
    return min(hits / 5, 1.0)


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