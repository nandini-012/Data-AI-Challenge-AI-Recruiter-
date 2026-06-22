import csv
import io
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.services.ranking_engine import rank_candidates

router = APIRouter()

@router.get("/rank")
def rank():
    """
    Ranks all loaded candidates and returns top 100 as JSON.
    """
    from app.main import candidates
    top100 = rank_candidates(candidates)
    return top100


@router.get("/rank/download")
def rank_download():
    """
    Downloads the top 100 ranking as a CSV file
    ready to submit to the challenge.
    """
    from app.main import candidates
    top100 = rank_candidates(candidates)

    # Build CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
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
