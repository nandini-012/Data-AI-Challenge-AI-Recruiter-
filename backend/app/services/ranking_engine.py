from datetime import date
from app.services.similarity_engine import (
    title_relevance_score,
    skill_match_score,
    career_substance_score,
    experience_fit_score,
    behavioral_multiplier
)
from app.services.skill_extractor import RELEVANT_SKILLS


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


def build_reasoning(candidate: dict, title_score: float,
                    career_score: float, days_inactive: int) -> str:
    profile = candidate.get("profile", {})
    title = profile.get("current_title", "")
    years = profile.get("years_of_experience", 0)
    skills = candidate.get("skills", [])

    # Title fit
    if title_score >= 1.0:
        parts = [f"currently {title}, a direct match for the target role"]
    elif title_score >= 0.7:
        parts = [f"currently {title}, an adjacent AI/ML role"]
    else:
        parts = [f"currently {title}, transitioning toward AI/ML based on skills"]

    # Top 2 relevant skills with longest duration
    rel_skills = [
        s for s in skills
        if any(r in (s.get("name") or "").lower() for r in RELEVANT_SKILLS)
    ]
    rel_skills_sorted = sorted(
        rel_skills,
        key=lambda s: s.get("duration_months", 0) or 0,
        reverse=True
    )
    if rel_skills_sorted:
        top_names = ", ".join(s["name"] for s in rel_skills_sorted[:2])
        parts.append(f"strongest skills: {top_names}")

    # Career substance
    if career_score >= 0.6:
        parts.append("production/deployment experience evident")
    elif career_score >= 0.3:
        parts.append("some production-facing work evident")

    parts.append(f"{years} years of experience")

    if days_inactive <= 30:
        parts.append("recently active on platform")
    elif days_inactive > 180:
        parts.append("note: inactive for extended period")

    return "; ".join(parts) + "."


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

        t_score = title_relevance_score(title)
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