from app.services.skill_extractor import extract_jd_keywords
from app.services.similarity_engine import (
    get_skill_score,
    get_experience_score,
    get_availability_score,
    get_location_score
)

def is_honeypot(candidate: dict) -> bool:
    """
    Detect impossible/fake profiles. The dataset has ~80 honeypots.
    If we rank them in top 100 we get disqualified.
    """
    career = candidate.get("career_history", [])
    for job in career:
        start = job.get("start_date", "")
        duration = job.get("duration_months", 0)
        # Check: does claimed duration match dates?
        if start and duration:
            try:
                from datetime import datetime
                start_date = datetime.fromisoformat(start)
                implied_end_months = duration
                # If duration > 120 months (10 years) at one company — suspicious
                if implied_end_months > 120:
                    return True
            except Exception:
                pass

    # Check for expert in too many skills with 0 months experience
    skills = candidate.get("skills", [])
    expert_zero_duration = sum(
        1 for s in skills
        if s.get("proficiency") == "advanced" and s.get("duration_months", 0) == 0
    )
    if expert_zero_duration >= 5:
        return True

    return False


def build_reasoning(candidate: dict, score: float, required_skills: set) -> str:
    """
    Build a 1-2 sentence reasoning for the submission CSV.
    Must be specific to each candidate — generic reasoning gets penalised.
    """
    profile = candidate.get("profile", {})
    name = profile.get("anonymized_name", "Candidate")
    years = profile.get("years_of_experience", 0)
    title = profile.get("current_title", "")
    company = profile.get("current_company", "")
    location = profile.get("location", "")

    # Find matched skills
    skills = candidate.get("skills", [])
    matched = [
        s["name"] for s in skills
        if s["name"].lower() in required_skills
    ]
    matched_str = ", ".join(matched[:3]) if matched else "adjacent skills"

    signals = candidate.get("redrob_signals", {})
    notice = signals.get("notice_period_days", "unknown")
    response = signals.get("recruiter_response_rate", 0)

    reasoning = (
        f"{years}yr {title} at {company} ({location}); "
        f"matched skills: {matched_str}. "
        f"Notice: {notice}d, response rate: {int(response*100)}%."
    )
    return reasoning


def score_candidate(candidate: dict, required_skills: set, bonus_skills: set) -> float:
    """
    Final score combining all signals.
    Weights are tuned based on what the JD actually cares about.
    """
    # Hard filter — skip honeypots entirely
    if is_honeypot(candidate):
        return -1.0

    skill_score = get_skill_score(candidate, required_skills, bonus_skills)
    experience_score = get_experience_score(candidate)
    availability_score = get_availability_score(candidate)
    location_score = get_location_score(candidate)

    # Weighted total — skills + experience matter most
    total = (
        skill_score * 0.40 +
        experience_score * 0.30 +
        availability_score * 0.20 +
        location_score * 0.10
    )

    return round(total, 4)


def rank_candidates(candidates: list) -> list:
    """
    Score all candidates and return top 100 with rank and reasoning.
    """
    required_skills, bonus_skills = extract_jd_keywords()
    scored = []

    for candidate in candidates:
        score = score_candidate(candidate, required_skills, bonus_skills)
        if score >= 0:  # skip honeypots (score = -1)
            scored.append({
                "candidate_id": candidate["candidate_id"],
                "score": score,
                "reasoning": build_reasoning(candidate, score, required_skills),
                "candidate": candidate
            })

    # Sort highest score first
    scored.sort(key=lambda x: x["score"], reverse=True)

    # Return top 100 with rank assigned
    top100 = []
    for rank, item in enumerate(scored[:100], start=1):
        top100.append({
            "rank": rank,
            "candidate_id": item["candidate_id"],
            "score": item["score"],
            "reasoning": item["reasoning"]
        })

    return top100
 