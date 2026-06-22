from datetime import datetime, date

# Companies the JD explicitly says NOT to hire from
# if that is their ONLY experience
SERVICES_COMPANIES = {
    "tcs", "infosys", "wipro", "accenture",
    "cognizant", "capgemini", "hexaware",
    "mindtree", "mphasis", "tech mahindra"
}

def get_skill_score(candidate: dict, required_skills: set, bonus_skills: set) -> float:
    """
    Score based on skills matched with JD.
    Checks skill name, proficiency level, and duration used.
    """
    score = 0.0
    skills = candidate.get("skills", [])

    for skill in skills:
        name = skill.get("name", "").lower()
        proficiency = skill.get("proficiency", "beginner")
        duration = skill.get("duration_months", 0)
        endorsements = skill.get("endorsements", 0)

        if name in required_skills:
            # Base points for matching required skill
            score += 10

            # More points for higher proficiency
            if proficiency == "advanced":
                score += 5
            elif proficiency == "intermediate":
                score += 3

            # More points for longer use
            if duration >= 24:
                score += 3
            elif duration >= 12:
                score += 1

            # More points if others endorsed this skill
            if endorsements >= 20:
                score += 2

        elif name in bonus_skills:
            score += 2

    return score


def get_experience_score(candidate: dict) -> float:
    """
    Score based on years of experience and type of companies worked at.
    JD wants 5-9 years at product companies, not consulting firms.
    """
    score = 0.0
    profile = candidate.get("profile", {})
    years = profile.get("years_of_experience", 0)

    # JD wants 5-9 years
    if 5 <= years <= 9:
        score += 20
    elif 4 <= years < 5:
        score += 15
    elif 9 < years <= 12:
        score += 10
    elif years < 4:
        score += 0

    # Check career history for product company experience
    career = candidate.get("career_history", [])
    only_services = True

    for job in career:
        company = job.get("company", "").lower()
        industry = job.get("industry", "").lower()
        duration = job.get("duration_months", 0)

        is_services = any(s in company for s in SERVICES_COMPANIES)

        if not is_services:
            only_services = False
            # Reward product company experience
            if duration >= 24:
                score += 8
            elif duration >= 12:
                score += 4

        # Check job description text for AI/ML work
        desc = job.get("description", "").lower()
        ai_keywords = [
            "embedding", "vector", "retrieval", "ranking",
            "recommendation", "search", "nlp", "llm",
            "machine learning", "ml model", "rag"
        ]
        for kw in ai_keywords:
            if kw in desc:
                score += 2
                break  # only count once per job

    # JD explicitly penalises those ONLY from services companies
    if only_services:
        score -= 15

    return score


def get_availability_score(candidate: dict) -> float:
    """
    Score based on redrob behavioral signals.
    A perfect-on-paper candidate who is inactive is not actually hireable.
    """
    score = 0.0
    signals = candidate.get("redrob_signals", {})

    # Is the candidate actively looking?
    if signals.get("open_to_work_flag") is True:
        score += 15

    # How recently were they active on the platform?
    last_active = signals.get("last_active_date", "")
    if last_active:
        try:
            last_date = datetime.fromisoformat(last_active).date()
            today = date(2026, 6, 21)  # current date
            days_inactive = (today - last_date).days
            if days_inactive <= 30:
                score += 15
            elif days_inactive <= 60:
                score += 10
            elif days_inactive <= 90:
                score += 5
            elif days_inactive > 180:
                score -= 10  # inactive for 6+ months = bad
        except Exception:
            pass

    # Recruiter response rate — how often do they reply?
    response_rate = signals.get("recruiter_response_rate", -1)
    if response_rate >= 0:
        score += response_rate * 15

    # Notice period — JD prefers under 30 days
    notice = signals.get("notice_period_days", 999)
    if notice <= 30:
        score += 10
    elif notice <= 60:
        score += 5
    elif notice > 90:
        score -= 5

    # Profile completeness
    completeness = signals.get("profile_completeness_score", 0)
    score += (completeness / 100) * 5

    # Interview completion rate
    interview_rate = signals.get("interview_completion_rate", -1)
    if interview_rate >= 0:
        score += interview_rate * 5

    return score


def get_location_score(candidate: dict) -> float:
    """
    JD prefers candidates in India, specifically Pune/Noida/Delhi NCR/Mumbai/Hyderabad.
    """
    score = 0.0
    profile = candidate.get("profile", {})
    country = profile.get("country", "").lower()
    location = profile.get("location", "").lower()

    preferred_cities = {
        "pune", "noida", "delhi", "mumbai",
        "hyderabad", "bangalore", "bengaluru"
    }

    if country == "india":
        score += 10
        if any(city in location for city in preferred_cities):
            score += 5

    # Willing to relocate helps
    signals = candidate.get("redrob_signals", {})
    if signals.get("willing_to_relocate") is True:
        score += 3

    return score 
