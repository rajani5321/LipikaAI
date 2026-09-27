from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.models.schemas import CandidateResponse, CandidateStatusUpdate
from app.db.client import db_manager

router = APIRouter(prefix="/candidates", tags=["Candidates"])

@router.get("/", response_model=List[CandidateResponse])
def get_candidates(
    search: Optional[str] = Query(None),
    skill: Optional[str] = Query(None),
    min_exp: Optional[float] = Query(None),
    max_exp: Optional[float] = Query(None),
    education: Optional[str] = Query(None),
    cand_status: Optional[str] = Query(None, alias="status")
):
    candidates = db_manager.candidates.find({})
    filtered = []
    
    target_skills = [s.strip().lower() for s in skill.split(",")] if skill else []
    
    for c in candidates:
        # Search filter
        if search:
            s_low = search.lower()
            cand_name = c.get("name", "").lower()
            cand_email = c.get("email", "").lower()
            cand_skills = " ".join(c.get("skills", [])).lower()
            if s_low not in cand_name and s_low not in cand_email and s_low not in cand_skills:
                continue

        # Skill filter
        if target_skills:
            cand_skills_lower = {s.lower() for s in c.get("skills", [])}
            if not any(ts in cand_skills_lower for ts in target_skills):
                continue

        # Experience filters
        exp = float(c.get("experience_years", 0.0))
        if min_exp is not None and exp < min_exp:
            continue
        if max_exp is not None and exp > max_exp:
            continue

        # Education filter
        if education and education.lower() not in c.get("education", "").lower():
            continue

        # Status filter
        if cand_status and c.get("status", "Active").lower() != cand_status.lower():
            continue

        filtered.append(CandidateResponse(
            id=str(c.get("id") or c.get("_id")),
            name=c.get("name", "Unknown"),
            email=c.get("email", ""),
            phone=c.get("phone", ""),
            skills=c.get("skills", []),
            experience_years=float(c.get("experience_years", 0.0)),
            education=c.get("education", "Not Specified"),
            summary=c.get("summary", ""),
            raw_text=c.get("raw_text", ""),
            resume_filename=c.get("resume_filename", ""),
            resume_path=c.get("resume_path", ""),
            uploaded_at=c.get("uploaded_at", ""),
            status=c.get("status", "Active")
        ))
        
    return filtered

@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: str):
    cand = db_manager.candidates.find_one({"id": candidate_id})
    if not cand:
        cand = db_manager.candidates.find_one({"_id": candidate_id})
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    return CandidateResponse(
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

@router.put("/{candidate_id}/status")
def update_candidate_status(candidate_id: str, status_in: CandidateStatusUpdate):
    cand = db_manager.candidates.find_one({"id": candidate_id})
    if not cand:
        cand = db_manager.candidates.find_one({"_id": candidate_id})
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")

    db_manager.candidates.update_one({"id": candidate_id}, {"$set": {"status": status_in.status}})
    db_manager.log_activity("Candidate Status", f"Updated status of {cand.get('name')} to '{status_in.status}'", "candidate")
    return {"message": "Status updated successfully", "id": candidate_id, "status": status_in.status}

@router.delete("/{candidate_id}")
def delete_candidate(candidate_id: str):
    res = db_manager.candidates.delete_one({"id": candidate_id})
    if res.deleted_count == 0:
        db_manager.candidates.delete_one({"_id": candidate_id})
    db_manager.log_activity("Delete Candidate", f"Deleted candidate {candidate_id}", "candidate")
    return {"message": "Candidate profile deleted successfully", "id": candidate_id}
