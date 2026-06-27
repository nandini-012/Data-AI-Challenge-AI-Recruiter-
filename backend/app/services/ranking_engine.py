from datetime import date
from app.services.similarity_engine import (
    title_relevance_score,
    skill_match_score,
    career_substance_score,
    experience_fit_score,
    behavioral_multiplier,
    has_junior_or_associate_title,
    has_title_experience_inconsistency
)
from app.services.skill_extractor import (
    is_relevant_skill,
    normalize_reasoning_skill_name,
    reasoning_skill_tier,
)


OPENING_REASON_TEMPLATES = {
    "senior": [
        "Strong shortlist profile with senior title alignment",
        "Senior-level profile with clear role fit",
        "High-confidence AI/ML profile led by seniority signal",
    ],
    "direct": [
        "Strong shortlist profile with direct title alignment",
        "Clear AI/ML fit from the current role",
        "High-confidence profile for the target AI/ML role",
    ],
    "junior": [
        "Relevant AI/ML profile, with seniority reviewed cautiously",
        "Useful AI/ML fit, tempered by junior-level title signal",
        "Promising profile with moderated seniority confidence",
    ],
    "adjacent": [
        "Adjacent AI/ML profile with transferable evidence",
        "Relevant profile with partial title alignment",
        "Transferable AI/ML fit supported by the broader profile",
    ],
    "transition": [
        "Potential fit where skills and career evidence carry the case",
        "Less direct title fit, with the profile evaluated through evidence",
        "Transition profile supported mainly by technical and career signals",
    ],
}

ROLE_FIT_REASON_TEMPLATES = {
    "senior": [
        "the current title is {title}",
        "{title} gives a senior-leaning match signal",
        "role fit is supported by the current title, {title}",
    ],
    "direct": [
        "the current title is {title}",
        "{title} maps directly to the target profile",
        "role fit is strong from the current title, {title}",
    ],
    "junior": [
        "the current title is {title}",
        "{title} shows relevance but carries a lighter seniority signal",
        "role relevance is present from {title}, with seniority adjusted",
    ],
    "adjacent": [
        "the current title is {title}",
        "{title} gives adjacent evidence for the target role",
        "role title suggests transferable AI/ML relevance: {title}",
    ],
    "transition": [
        "the current title is {title}",
        "{title} is less direct, so skills and career evidence matter more",
        "title fit is lighter from {title}",
    ],
}

SKILL_REASON_TEMPLATES = [
    "Differentiating technical evidence includes {skills}",
    "The strongest displayed skill signals are {skills}",
    "Technical depth is led by {skills}",
    "Skill evidence is strongest around {skills}",
    "Recruiter-visible differentiators include {skills}",
]

CORE_SKILL_REASON_TEMPLATES = [
    "Core technical coverage includes {skills}",
    "Foundational skill evidence includes {skills}",
    "Core matching skills show up as {skills}",
    "Baseline technical fit is supported by {skills}",
    "Foundational fit is visible through {skills}",
]

CAREER_REASON_TEMPLATES = {
    "strong": [
        "career history shows strong production engineering evidence",
        "work history includes meaningful production and deployment signals",
        "career descriptions point to applied engineering delivery",
        "production-facing execution is clear in the career record",
        "career evidence supports hands-on delivery in real systems",
    ],
    "some": [
        "career history includes some production-facing evidence",
        "some engineering delivery signals appear in prior roles",
        "career record has partial evidence of applied system work",
        "there are useful but lighter production signals in the history",
        "prior work shows some practical implementation evidence",
    ],
    "limited": [
        "career evidence is less production-heavy",
        "production signal is limited in the available descriptions",
        "career descriptions provide lighter engineering evidence",
        "hands-on production context is not strongly expressed",
        "career substance is driven more by title and skills than descriptions",
    ],
}

EXPERIENCE_REASON_TEMPLATES = {
    "early": [
        "{years} years of experience, below the target seniority band",
        "{years} years of experience, an earlier-career profile for this role",
        "experience is lighter at {years} years",
        "{years} years suggests a developing experience base",
        "seniority is still emerging at {years} years",
    ],
    "near": [
        "{years} years of experience, close to the target band",
        "{years} years gives near-fit seniority",
        "experience is approaching the target range at {years} years",
        "{years} years provides a plausible ramp into the role",
        "seniority is adjacent to target at {years} years",
    ],
    "target": [
        "{years} years of experience, inside the target band",
        "{years} years matches the preferred experience range",
        "experience fit is strong at {years} years",
        "{years} years gives the right seniority balance",
        "target-band experience is present at {years} years",
    ],
    "above": [
        "{years} years of experience, slightly above the target band",
        "{years} years indicates a more senior profile than requested",
        "experience is above target but still relevant at {years} years",
        "{years} years brings additional seniority",
        "seniority runs higher than target at {years} years",
    ],
}

ACTIVITY_REASON_TEMPLATES = {
    "recent": [
        "recently active on platform",
        "recent platform activity improves availability signal",
        "activity recency is strong",
        "recent engagement supports recruiter reachability",
        "platform activity is current",
    ],
    "moderate": [
        "platform activity is not very recent but still usable",
        "activity signal is moderate",
        "recency is acceptable but not a top signal",
        "engagement is present with some recency gap",
        "platform activity is neither fresh nor stale",
    ],
    "inactive": [
        "note: inactive for extended period",
        "extended inactivity lowers behavioral confidence",
        "platform recency is weak",
        "availability signal is reduced by inactivity",
        "behavioral signal is cautious due to inactivity",
    ],
}

CLOSING_REASON_TEMPLATES = {
    "strong": [
        "Good recruiter priority for the top slate",
        "Worth prioritizing for outreach",
        "Strong candidate to advance for review",
    ],
    "balanced": [
        "Worth reviewing against the final role bar",
        "Reasonable profile to keep in the shortlist",
        "Useful candidate to compare with stronger production profiles",
    ],
    "cautious": [
        "Review carefully against seniority and availability needs",
        "Best treated as a cautious shortlist option",
        "Needs recruiter review on the weaker signals",
    ],
}


def _template_index(candidate_id: str, options: list, salt: str = "") -> int:
    if not options:
        return 0
    key = f"{candidate_id or ''}:{salt}"
    return sum(ord(ch) for ch in key) % len(options)


def _choose_template(candidate_id: str, options: list, salt: str = "") -> str:
    return options[_template_index(candidate_id, options, salt)]


def is_honeypot(candidate: dict) -> bool:
    """
    5 checks exactly matching Ravi's validated pipeline.
    """
    cid = candidate["candidate_id"]
    profile = candidate.get("profile", {})
    exp_months = (profile.get("years_of_experience", 0) or 0) * 12
    skills = candidate.get("skills", [])
    career = candidate.get("career_history", [])
    education = candidate.get("education", [])

    flags = 0

    # 1. Skill duration exceeds total experience
    for s in skills:
        dm = s.get("duration_months", 0) or 0
        if dm > exp_months + 24:
            flags += 1
            break

    # 2. Expert proficiency with near-zero duration
    for s in skills:
        if s.get("proficiency") == "expert" and (s.get("duration_months", 0) or 0) <= 2:
            flags += 1
            break

    # 3. Career months mismatch vs years of experience
    career_months = sum(j.get("duration_months", 0) or 0 for j in career)
    if abs(career_months - exp_months) > 48:
        flags += 1

    # 4. Multiple simultaneous current jobs
    current_jobs = [j for j in career if j.get("is_current")]
    if len(current_jobs) > 1:
        flags += 1

    # 5. Education end_year before start_year
    for e in education:
        if e.get("end_year") and e.get("start_year") and e["end_year"] < e["start_year"]:
            flags += 1
            break

    return flags >= 2


def get_days_since_active(signals: dict) -> int:
    last_active = signals.get("last_active_date", "")
    if not last_active:
        return 999
    try:
        from datetime import datetime
        last_date = datetime.fromisoformat(last_active).date()
        today = date.today()
        return (today - last_date).days
    except Exception:
        return 999


def _title_bucket(title: str, title_score: float) -> str:
    title_l = (title or "").lower()
    if has_junior_or_associate_title(title):
        return "junior"
    if any(term in title_l for term in ("senior", "staff", "principal", "lead", "head")):
        return "senior"
    if title_score >= 0.85:
        return "direct"
    if title_score >= 0.6:
        return "adjacent"
    return "transition"


def _experience_bucket(years: float) -> str:
    if years < 3:
        return "early"
    if years < 5:
        return "near"
    if years <= 9:
        return "target"
    return "above"


def _activity_bucket(days_inactive: int) -> str:
    if days_inactive <= 30:
        return "recent"
    if days_inactive > 180:
        return "inactive"
    return "moderate"


def _career_bucket(career_score: float) -> str:
    if career_score >= 0.6:
        return "strong"
    if career_score >= 0.3:
        return "some"
    return "limited"


def _closing_bucket(title_bucket: str, career_bucket: str,
                    experience_bucket: str, activity_bucket: str) -> str:
    if activity_bucket == "inactive" or experience_bucket == "early":
        return "cautious"
    if title_bucket in ("senior", "direct") and career_bucket == "strong":
        return "strong"
    return "balanced"


def _format_years(years: float) -> str:
    if isinstance(years, float):
        return f"{years:.1f}".rstrip("0").rstrip(".")
    return str(years)


def _selected_reasoning_skills(skills: list) -> tuple:
    tiered_skills = {"differentiator": [], "core": []}
    seen = set()

    for skill in sorted(
        skills,
        key=lambda s: s.get("duration_months", 0) or 0,
        reverse=True,
    ):
        name = skill.get("name") or ""
        if not is_relevant_skill(name) and not reasoning_skill_tier(name):
            continue

        display_name = normalize_reasoning_skill_name(name)
        tier = reasoning_skill_tier(display_name)
        if tier not in tiered_skills or display_name in seen:
            continue

        seen.add(display_name)
        tiered_skills[tier].append(display_name)

    if tiered_skills["differentiator"]:
        return tiered_skills["differentiator"][:2], "differentiator"
    return tiered_skills["core"][:2], "core"


def build_reasoning(candidate: dict, title_score: float,
                    career_score: float, days_inactive: int) -> str:
    profile = candidate.get("profile", {})
    title = profile.get("current_title", "")
    years = profile.get("years_of_experience", 0)
    skills = candidate.get("skills", [])
    candidate_id = candidate.get("candidate_id", "")

    title_bucket = _title_bucket(title, title_score)
    opening_template = _choose_template(
        candidate_id,
        OPENING_REASON_TEMPLATES[title_bucket],
        "opening",
    )
    role_template = _choose_template(
        candidate_id,
        ROLE_FIT_REASON_TEMPLATES[title_bucket],
        "role",
    )
    sentences = [
        (
            f"{opening_template}; "
            f"{role_template.format(title=title or 'the current role')}."
        )
    ]

    skill_names, skill_tier = _selected_reasoning_skills(skills)
    evidence_parts = []
    if skill_names:
        skill_templates = (
            SKILL_REASON_TEMPLATES
            if skill_tier == "differentiator"
            else CORE_SKILL_REASON_TEMPLATES
        )
        skill_template = _choose_template(candidate_id, skill_templates, "skills")
        evidence_parts.append(skill_template.format(skills=", ".join(skill_names)))

    career_bucket = _career_bucket(career_score)
    career_template = _choose_template(
        candidate_id,
        CAREER_REASON_TEMPLATES[career_bucket],
        "career",
    )
    evidence_parts.append(career_template)
    sentences.append("; ".join(evidence_parts) + ".")

    experience_bucket = _experience_bucket(years)
    experience_template = _choose_template(
        candidate_id,
        EXPERIENCE_REASON_TEMPLATES[experience_bucket],
        "experience",
    )

    activity_bucket = _activity_bucket(days_inactive)
    activity_template = _choose_template(
        candidate_id,
        ACTIVITY_REASON_TEMPLATES[activity_bucket],
        "behavior",
    )
    closing_bucket = _closing_bucket(
        title_bucket,
        career_bucket,
        experience_bucket,
        activity_bucket,
    )
    closing_template = _choose_template(
        candidate_id,
        CLOSING_REASON_TEMPLATES[closing_bucket],
        "closing",
    )
    sentences.append(
        (
            f"{experience_template.format(years=_format_years(years))}; "
            f"{activity_template}. {closing_template}."
        )
    )

    return " ".join(sentences)


def rank_candidates(candidates: list) -> list:
    scored = []

    for candidate in candidates:
        if is_honeypot(candidate):
            continue

        profile = candidate.get("profile", {})
        signals = candidate.get("redrob_signals", {})
        skills = candidate.get("skills", [])
        career = candidate.get("career_history", [])

        title = profile.get("current_title", "")
        years = profile.get("years_of_experience", 0) or 0
        days_inactive = get_days_since_active(signals)

        title_inconsistency = has_title_experience_inconsistency(title, years)
        t_score = title_relevance_score(title, years)
        s_score = skill_match_score(skills)
        c_score = career_substance_score(career)
        e_score = experience_fit_score(years)
        b_mult = behavioral_multiplier(signals, days_inactive)

        base_score = (
            0.35 * t_score +
            0.30 * s_score +
            0.20 * c_score +
            0.15 * e_score
        )
        final_score = round(base_score * b_mult, 4)
        if title_inconsistency:
            final_score = round(final_score * 0.97, 4)

        scored.append({
            "candidate_id": candidate["candidate_id"],
            "score": final_score,
            "reasoning": build_reasoning(candidate, t_score, c_score, days_inactive)
        })

    # Sort by score desc, candidate_id asc for tie-breaking
    scored.sort(key=lambda x: (-x["score"], x["candidate_id"]))

    # Assign ranks
    top100 = []
    for rank, item in enumerate(scored[:100], start=1):
        top100.append({
            "candidate_id": item["candidate_id"],
            "rank": rank,
            "score": item["score"],
            "reasoning": item["reasoning"]
        })

    return top100 
