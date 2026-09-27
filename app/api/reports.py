import csv
import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.db.client import db_manager
from app.services.matching_engine import matching_engine

router = APIRouter(prefix="/reports", tags=["HR Reports & Exports"])

@router.get("/job/{job_id}/csv")
def export_job_candidates_csv(job_id: str):
    """Generates and streams a downloadable CSV report of candidates ranked for a job."""
    job = db_manager.jobs.find_one({"id": job_id}) or db_manager.jobs.find_one({"_id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    candidates = db_manager.candidates.find({})
    ranked = matching_engine.rank_candidates_for_job(job, candidates)

    output = io.StringIO()
    writer = csv.writer(output)

    # Header Row
    writer.writerow([
        "Rank",
        "Candidate Name",
        "Email",
        "Phone",
        "Overall Score (%)",
        "Skill Score (%)",
        "Semantic Score (%)",
        "Experience Score (%)",
        "Education Score (%)",
        "Experience (Years)",
        "Education",
        "Recommendation",
        "Matched Core Skills",
        "Missing Core Skills",
        "HR Verdict"
    ])

    for idx, r in enumerate(ranked, start=1):
        c = r.candidate
        m = r.match
        writer.writerow([
            idx,
            c.name,
            c.email,
            c.phone,
            m.overall_score,
            m.skill_score,
            m.semantic_score,
            m.experience_score,
            m.education_score,
            c.experience_years,
            c.education,
            m.recommendation,
            "; ".join(m.matched_required_skills),
            "; ".join(m.missing_required_skills),
            m.verdict
        ])

    output.seek(0)
    filename = f"candidates_report_{job.get('title', 'job').replace(' ', '_').lower()}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
