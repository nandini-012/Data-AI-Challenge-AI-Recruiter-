import csv
import hashlib
import io
import json
import time
from collections import Counter
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.routes.jd_routes import get_jd
from app.services.ranking_engine import rank_candidates
from app.services.skill_extractor import parse_jd_context

router = APIRouter()

_rank_cache = {}

_analytics_cache = {
    "source_size": None,
    "dashboard_by_jd": {},
    "analytics": None,
}


def _normalize_jd(jd=None):
    if not jd:
        return get_jd()

    try:
        return json.loads(jd)
    except json.JSONDecodeError:
        return {"job_description": jd}


def _jd_hash(jd=None):
    payload = _normalize_jd(jd)
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _get_rank_bundle(candidates, jd=None):
    cache_key = _jd_hash(jd)
    cached = _rank_cache.get(cache_key)

    if cached is not None and cached["source_size"] == len(candidates):
        print(f"Cache hit ({cache_key[:8]})")
        return cached

    print(f"\nGenerating ranking for {len(candidates):,} candidates")

    total = time.time()

    t = time.time()
    jd_payload = _normalize_jd(jd)
    jd_context = parse_jd_context(jd_payload)
    print(f"JD parsing: {time.time()-t:.2f}s")

    rank_start = time.time()
    ranked = rank_candidates(candidates, jd_context)
    print(f"Ranking: {time.time()-rank_start:.2f}s")

    cached = {
        "source_size": len(candidates),
        "ranked": ranked,
        "ranked_by_id": {
            item["candidate_id"]: item
            for item in ranked
        },
    }

    _rank_cache[cache_key] = cached

    print(f"TOTAL: {time.time()-total:.2f}s\n")

    return cached


def _get_candidate_index():
    from app.main import candidate_index

    return candidate_index


def _get_ranked(candidates, jd=None):
    return _get_rank_bundle(candidates, jd)["ranked"]


def _get_ranked_by_id(candidates, jd=None):
    return _get_rank_bundle(candidates, jd)["ranked_by_id"]


def _refresh_analytics_cache(candidates):
    if _analytics_cache["source_size"] != len(candidates):
        _analytics_cache["source_size"] = len(candidates)
        _analytics_cache["dashboard_by_jd"] = {}
        _analytics_cache["analytics"] = None


def _candidate_profile(candidate):
    return candidate.get("profile", {}) or {}


def _candidate_signals(candidate):
    return candidate.get("redrob_signals", {}) or {}


def _candidate_skills(candidate):
    return candidate.get("skills", []) or []


def _candidate_career(candidate):
    return candidate.get("career_history", []) or []


def _avg(values):
    values = [value for value in values if isinstance(value, (int, float))]
    return round(sum(values) / len(values), 2) if values else 0


def _top_counter(counter, limit=10):
    return [
        {"name": name, "count": count}
        for name, count in counter.most_common(limit)
    ]


def _build_dashboard(candidates, ranked):
    skill_counter = Counter()
    role_counter = Counter()

    for candidate in candidates:
        profile = _candidate_profile(candidate)
        title = profile.get("current_title")
        if title:
            role_counter[title] += 1

        for skill in _candidate_skills(candidate):
            name = skill.get("name")
            if name:
                skill_counter[name] += 1

    return {
        "total_candidates": len(candidates),
        "shortlisted_candidates": len(ranked),
        "average_experience": _avg(
            (_candidate_profile(candidate).get("years_of_experience") or 0)
            for candidate in candidates
        ),
        "average_score": _avg(item.get("score") for item in ranked),
        "most_common_skills": _top_counter(skill_counter, limit=10),
        "role_distribution": _top_counter(role_counter, limit=10),
    }


def _experience_bucket(years):
    if years < 3:
        return "0-2"
    if years < 5:
        return "3-4"
    if years <= 9:
        return "5-9"
    if years <= 12:
        return "10-12"
    return "13+"


def _build_analytics(candidates):
    experience_counter = Counter()
    role_counter = Counter()
    skill_counter = Counter()
    open_to_work = 0
    verified_email = 0
    verified_phone = 0
    response_rates = []
    response_times = []
    interview_rates = []

    for candidate in candidates:
        profile = _candidate_profile(candidate)
        signals = _candidate_signals(candidate)

        years = profile.get("years_of_experience") or 0
        experience_counter[_experience_bucket(years)] += 1

        title = profile.get("current_title")
        if title:
            role_counter[title] += 1

        for skill in _candidate_skills(candidate):
            name = skill.get("name")
            if name:
                skill_counter[name] += 1

        if signals.get("open_to_work_flag"):
            open_to_work += 1
        if signals.get("verified_email"):
            verified_email += 1
        if signals.get("verified_phone"):
            verified_phone += 1

        response_rates.append(signals.get("recruiter_response_rate") or 0)
        response_times.append(signals.get("avg_response_time_hours") or 0)
        interview_rates.append(signals.get("interview_completion_rate") or 0)

    return {
        "experience_distribution": [
            {"range": name, "count": experience_counter.get(name, 0)}
            for name in ["0-2", "3-4", "5-9", "10-12", "13+"]
        ],
        "role_distribution": _top_counter(role_counter, limit=20),
        "skill_frequency": _top_counter(skill_counter, limit=20),
        "behavior_statistics": {
            "open_to_work_candidates": open_to_work,
            "verified_email_candidates": verified_email,
            "verified_phone_candidates": verified_phone,
            "average_recruiter_response_rate": _avg(response_rates),
            "average_response_time_hours": _avg(response_times),
            "average_interview_completion_rate": _avg(interview_rates),
        },
    }


def _lightweight_candidate(candidate, ranked_by_id):
    profile = _candidate_profile(candidate)
    ranked = ranked_by_id.get(candidate.get("candidate_id"), {})
    return {
        "candidate_id": candidate.get("candidate_id"),
        "current_title": profile.get("current_title", ""),
        "current_company": profile.get("current_company", ""),
        "years_of_experience": profile.get("years_of_experience", 0),
        "location": profile.get("location", ""),
        "country": profile.get("country", ""),
        "skills": [
            skill.get("name")
            for skill in _candidate_skills(candidate)[:8]
            if skill.get("name")
        ],
        "rank": ranked.get("rank"),
        "score": ranked.get("score"),
        "reasoning": ranked.get("reasoning"),
    }


def _candidate_matches(candidate, ranked, query):
    profile = _candidate_profile(candidate)
    query = query.lower()

    searchable_values = [
        candidate.get("candidate_id", ""),
        profile.get("current_title", ""),
        str(profile.get("years_of_experience", "")),
        ranked.get("reasoning", "") if ranked else "",
    ]

    searchable_values.extend(
        skill.get("name", "") for skill in _candidate_skills(candidate)
    )
    searchable_values.extend(
        job.get("company", "") for job in _candidate_career(candidate)
    )

    return any(query in str(value).lower() for value in searchable_values)


@router.get("/dashboard")
def dashboard(jd: str = Query(None)):
    from app.main import candidates

    jd_cache_key = _jd_hash(jd)
    ranked = _get_ranked(candidates, jd)
    _refresh_analytics_cache(candidates)
    if jd_cache_key not in _analytics_cache["dashboard_by_jd"]:
        _analytics_cache["dashboard_by_jd"][jd_cache_key] = _build_dashboard(
            candidates,
            ranked,
        )
    return _analytics_cache["dashboard_by_jd"][jd_cache_key]


@router.get("/rank")
def rank(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    jd: str = Query(None),
):
    from app.main import candidates

    ranked = _get_ranked(candidates, jd)
    start = (page - 1) * limit
    end = start + limit
    return {
        "page": page,
        "limit": limit,
        "total": len(ranked),
        "total_pages": (len(ranked) + limit - 1) // limit,
        "candidates": ranked[start:end],
    }


@router.get("/candidate/{candidate_id}")
def candidate_details(candidate_id: str, jd: str = Query(None)):
    from app.main import candidates

    candidate = _get_candidate_index().get(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    ranked_by_id = _get_ranked_by_id(candidates, jd)
    return {
        "candidate": candidate,
        "ranking": ranked_by_id.get(candidate_id),
        "is_shortlisted": candidate_id in ranked_by_id,
    }


@router.get("/search")
def search(
    q: str = Query("", min_length=0),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    jd: str = Query(None),
):
    from app.main import candidates

    query = q.strip()
    ranked_by_id = _get_ranked_by_id(candidates, jd)

    if not query:
        return {
            "q": q,
            "page": page,
            "limit": limit,
            "total": 0,
            "total_pages": 0,
            "candidates": [],
        }

    total = 0
    page_items = []
    start = (page - 1) * limit
    end = start + limit

    for candidate in candidates:
        ranked_item = ranked_by_id.get(candidate.get("candidate_id"), {})
        if _candidate_matches(candidate, ranked_item, query):
            if start <= total < end:
                page_items.append(_lightweight_candidate(candidate, ranked_by_id))
            total += 1

    return {
        "q": q,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit,
        "candidates": page_items,
    }


@router.get("/analytics")
def analytics(jd: str = Query(None)):
    from app.main import candidates

    _get_ranked(candidates, jd)
    _refresh_analytics_cache(candidates)
    if (
        _analytics_cache["analytics"] is None
    ):
        _analytics_cache["analytics"] = _build_analytics(candidates)
    return _analytics_cache["analytics"]


@router.get("/rank/download")
def rank_download(jd: str = Query(None)):
    from app.main import candidates
    top100 = _get_ranked(candidates, jd)

    output = io.StringIO()
    writer = csv.writer(output)

    # Exact column order required by validator
    writer.writerow(["candidate_id", "rank", "score", "reasoning"])

    for item in top100:
        writer.writerow([
            item["candidate_id"],
            item["rank"],
            item["score"],
            item["reasoning"]
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=submission.csv"}
    ) 
