import csv
import io
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.services.ranking_engine import rank_candidates

router = APIRouter()


@router.get("/rank")
def rank():
    from app.main import candidates
    return rank_candidates(candidates)


@router.get("/rank/download")
def rank_download():
    from app.main import candidates
    top100 = rank_candidates(candidates)

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