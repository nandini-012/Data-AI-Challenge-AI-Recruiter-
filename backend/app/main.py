import os
from fastapi import FastAPI
from dotenv import load_dotenv
from app.services.resume_parser import load_candidates
from app.routes import ranking_routes, jd_routes, resume_routes

load_dotenv()

app = FastAPI(title="AI Recruiter — Redrob Challenge")

app.include_router(ranking_routes.router)
app.include_router(jd_routes.router)
app.include_router(resume_routes.router)

DATA_PATH = os.getenv("DATA_PATH", "data/candidates.jsonl")
print(f"Loading candidates from {DATA_PATH} ...")
candidates = load_candidates(DATA_PATH)
print(f"Loaded {len(candidates)} candidates successfully!")


@app.get("/")
def root():
    return {
        "status": "ok",
        "candidates_loaded": len(candidates),
        "endpoints": {
            "rank_json": "/rank",
            "download_csv": "/rank/download",
            "jd_info": "/jd",
            "resume_count": "/resumes/count",
            "resume_sample": "/resumes/sample"
        }
    } 
