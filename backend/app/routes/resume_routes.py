from fastapi import APIRouter

router = APIRouter()

@router.get("/resumes/count")
def count_resumes():
    from app.main import candidates
    return {"total_candidates": len(candidates)}


@router.get("/resumes/sample")
def sample_resumes():
    from app.main import candidates
    return candidates[:5]  # return first 5 candidates as preview 
