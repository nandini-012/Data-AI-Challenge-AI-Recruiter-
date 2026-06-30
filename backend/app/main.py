import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware   # ← NEW
from dotenv import load_dotenv
from app.services.resume_parser import load_candidates
from app.routes import ranking_routes, jd_routes, resume_routes

load_dotenv()

# Global candidates list
candidates = []
candidate_index = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load candidates once at startup.
    Proper FastAPI lifespan pattern.
    """
    global candidates, candidate_index
    DATA_PATH = os.getenv("DATA_PATH", "data/candidates.jsonl")
    print(f"Loading candidates from {DATA_PATH} ...")
    candidates = load_candidates(DATA_PATH)
    candidate_index = {
        candidate.get("candidate_id"): candidate
        for candidate in candidates
        if candidate.get("candidate_id")
    }
    print(f"Loaded {len(candidates)} candidates successfully!")
    print(f"Built candidate index with {len(candidate_index)} entries.")
    yield
    candidates.clear()
    candidate_index.clear()
    print("Server shutdown — candidates cleared.")


app = FastAPI(
    title="AI Recruiter — Redrob Challenge",
    description="Ranks 100,000 candidates against a job description intelligently.",
    version="1.0.0",
    lifespan=lifespan
)

# ── CORS — allow frontend to call backend ──────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # all origins (safe for local dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ───────────────────────────────────────────────────────

app.include_router(ranking_routes.router, tags=["Ranking"])
app.include_router(jd_routes.router, tags=["Job Description"])
app.include_router(resume_routes.router, tags=["Resumes"])


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "candidates_loaded": len(candidates),
        "endpoints": {
            "rank_json": "/rank",
            "download_csv": "/rank/download",
            "jd_info": "/jd",
            "resume_count": "/resumes/count",
            "resume_sample": "/resumes/sample",
            "api_docs": "/docs"
        }
    }


@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "healthy",
        "candidates_loaded": len(candidates)
    }
