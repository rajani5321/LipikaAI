import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Query
from app.models.schemas import JobCreate, JobUpdate, JobResponse
from app.db.client import db_manager

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/", response_model=List[JobResponse])
def get_jobs(status_filter: Optional[str] = Query(None, alias="status")):
    query = {}
    if status_filter:
        query["status"] = status_filter
    
    jobs = db_manager.jobs.find(query)
    candidate_count = db_manager.candidates.count_documents({})
    
    result = []
    for job in jobs:
        result.append(JobResponse(
            id=str(job.get("id") or job.get("_id")),
            title=job.get("title", ""),
            department=job.get("department", "Engineering"),
            required_skills=job.get("required_skills", []),
            preferred_skills=job.get("preferred_skills", []),
            min_experience=float(job.get("min_experience", 0.0)),
            education_level=job.get("education_level", "Bachelor"),
            description=job.get("description", ""),
            status=job.get("status", "Active"),
            created_at=job.get("created_at", datetime.utcnow().strftime("%Y-%m-%d")),
            candidate_count=candidate_count
        ))
    return result

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str):
    job = db_manager.jobs.find_one({"id": job_id})
    if not job:
        job = db_manager.jobs.find_one({"_id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job vacancy not found")
        
    candidate_count = db_manager.candidates.count_documents({})
    return JobResponse(
        id=str(job.get("id") or job.get("_id")),
        title=job.get("title", ""),
        department=job.get("department", "Engineering"),
        required_skills=job.get("required_skills", []),
        preferred_skills=job.get("preferred_skills", []),
        min_experience=float(job.get("min_experience", 0.0)),
        education_level=job.get("education_level", "Bachelor"),
        description=job.get("description", ""),
        status=job.get("status", "Active"),
        created_at=job.get("created_at", datetime.utcnow().strftime("%Y-%m-%d")),
        candidate_count=candidate_count
    )

@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job_in: JobCreate):
    new_job = {
        "id": str(uuid.uuid4()),
        "title": job_in.title,
        "department": job_in.department,
        "required_skills": [s.strip() for s in job_in.required_skills if s.strip()],
        "preferred_skills": [s.strip() for s in job_in.preferred_skills if s.strip()],
        "min_experience": job_in.min_experience,
        "education_level": job_in.education_level,
        "description": job_in.description,
        "status": job_in.status,
        "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    }
    db_manager.jobs.insert_one(new_job)
    db_manager.log_activity("Create Job", f"Created job opening '{new_job['title']}'", "jobs")
    
    return JobResponse(
        **new_job,
        candidate_count=db_manager.candidates.count_documents({})
    )

@router.put("/{job_id}", response_model=JobResponse)
def update_job(job_id: str, job_update: JobUpdate):
    job = db_manager.jobs.find_one({"id": job_id})
    if not job:
        job = db_manager.jobs.find_one({"_id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    update_data = {k: v for k, v in job_update.model_dump().items() if v is not None}
    if update_data:
        db_manager.jobs.update_one({"id": job_id}, {"$set": update_data})
        db_manager.log_activity("Update Job", f"Updated job vacancy '{job.get('title')}'", "jobs")

    updated_job = db_manager.jobs.find_one({"id": job_id}) or job
    return JobResponse(
        id=str(updated_job.get("id") or updated_job.get("_id")),
        title=updated_job.get("title", ""),
        department=updated_job.get("department", "Engineering"),
        required_skills=updated_job.get("required_skills", []),
        preferred_skills=updated_job.get("preferred_skills", []),
        min_experience=float(updated_job.get("min_experience", 0.0)),
        education_level=updated_job.get("education_level", "Bachelor"),
        description=updated_job.get("description", ""),
        status=updated_job.get("status", "Active"),
        created_at=updated_job.get("created_at", ""),
        candidate_count=db_manager.candidates.count_documents({})
    )

@router.delete("/{job_id}")
def delete_job(job_id: str):
    res = db_manager.jobs.delete_one({"id": job_id})
    if res.deleted_count == 0:
        db_manager.jobs.delete_one({"_id": job_id})
    db_manager.log_activity("Delete Job", f"Deleted job vacancy {job_id}", "jobs")
    return {"message": "Job deleted successfully", "id": job_id}
