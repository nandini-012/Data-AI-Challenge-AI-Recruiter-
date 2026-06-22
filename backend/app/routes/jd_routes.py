from fastapi import APIRouter

router = APIRouter()

@router.get("/jd")
def get_jd():
    return {
        "role": "Senior AI Engineer — Founding Team",
        "company": "Redrob AI",
        "location": "Pune/Noida, India",
        "experience": "5-9 years",
        "must_have_skills": [
            "embeddings-based retrieval",
            "vector databases",
            "Python",
            "ranking system evaluation (NDCG, MRR, MAP)"
        ]
    } 
