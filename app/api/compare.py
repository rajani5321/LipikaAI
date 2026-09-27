from fastapi import APIRouter, HTTPException
from app.models.schemas import CompareRequest, CompareResult, CandidateComparisonItem, CandidateResponse, JobResponse
from app.services.matching_engine import matching_engine
from app.db.client import db_manager

router = APIRouter(prefix="/compare", tags=["Candidate Comparison"])

@router.post("/", response_model=CompareResult)
def compare_candidates(payload: CompareRequest):
    """
    Performs side-by-side comparative analysis of 2 or more candidates
    against a targeted job vacancy.
    """
    job = db_manager.jobs.find_one({"id": payload.job_id}) or db_manager.jobs.find_one({"_id": payload.job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job vacancy not found")

    if len(payload.candidate_ids) < 2:
        raise HTTPException(status_code=400, detail="Please select at least 2 candidates to compare")

    comparison_items = []
    
    for cand_id in payload.candidate_ids:
        cand = db_manager.candidates.find_one({"id": cand_id}) or db_manager.candidates.find_one({"_id": cand_id})
        if not cand:
            continue

        match = matching_engine.match_candidate_to_job(job, cand)
        
        # Calculate distinct strengths
        strengths = []
        if len(match.matched_required_skills) == len(job.get("required_skills", [])):
            strengths.append("100% Core Required Skills Matched")
        elif len(match.matched_required_skills) > 0:
            strengths.append(f"{len(match.matched_required_skills)} Required Skills Verified")

        if float(cand.get("experience_years", 0.0)) >= float(job.get("min_experience", 0.0)):
            strengths.append(f"Exceeds/Meets Experience Benchmark ({cand.get('experience_years')} yrs)")

        if match.semantic_score >= 70.0:
            strengths.append("High Resume-to-Job Contextual Relevance")

        if match.matched_preferred_skills:
            strengths.append(f"Possesses Preferred Skills: {', '.join(match.matched_preferred_skills)}")

        # Calculate gaps
        gaps = []
        if match.missing_required_skills:
            gaps.append(f"Missing Essential Skills: {', '.join(match.missing_required_skills)}")

        if float(cand.get("experience_years", 0.0)) < float(job.get("min_experience", 0.0)):
            gaps.append(f"Experience below requirement ({cand.get('experience_years')} yrs vs {job.get('min_experience')} yrs)")

        cand_resp = CandidateResponse(
            id=str(cand.get("id") or cand.get("_id")),
            name=cand.get("name", "Unknown"),
            email=cand.get("email", ""),
            phone=cand.get("phone", ""),
            skills=cand.get("skills", []),
            experience_years=float(cand.get("experience_years", 0.0)),
            education=cand.get("education", "Not Specified"),
            summary=cand.get("summary", ""),
            raw_text=cand.get("raw_text", ""),
            resume_filename=cand.get("resume_filename", ""),
            resume_path=cand.get("resume_path", ""),
            uploaded_at=cand.get("uploaded_at", ""),
            status=cand.get("status", "Active")
        )

        comparison_items.append(CandidateComparisonItem(
            candidate=cand_resp,
            match=match,
            strengths=strengths,
            gaps=gaps
        ))

    if not comparison_items:
        raise HTTPException(status_code=404, detail="None of the specified candidates were found")

    # Determine highest ranked candidate
    comparison_items.sort(key=lambda x: x.match.overall_score, reverse=True)
    top_candidate = comparison_items[0]

    job_resp = JobResponse(
        id=str(job.get("id") or job.get("_id")),
        title=job.get("title", ""),
        department=job.get("department", "Engineering"),
        required_skills=job.get("required_skills", []),
        preferred_skills=job.get("preferred_skills", []),
        min_experience=float(job.get("min_experience", 0.0)),
        education_level=job.get("education_level", "Bachelor"),
        description=job.get("description", ""),
        status=job.get("status", "Active"),
        created_at=job.get("created_at", ""),
        candidate_count=len(comparison_items)
    )

    hr_summary = (
        f"Based on automated multi-attribute analysis, {top_candidate.candidate.name} is the top match "
        f"with an overall score of {top_candidate.match.overall_score}%. "
        f"{top_candidate.candidate.name} covers {len(top_candidate.match.matched_required_skills)} required skills "
        f"and {top_candidate.candidate.experience_years} years of professional experience."
    )

    return CompareResult(
        job=job_resp,
        candidates=comparison_items,
        top_candidate_id=top_candidate.candidate.id,
        hr_recommendation_summary=hr_summary
    )
