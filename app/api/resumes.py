import os
import uuid
import shutil
from typing import List, Optional
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from app.config import UPLOAD_DIR, ALLOWED_EXTENSIONS
from app.services.document_parser import document_parser
from app.services.nlp_extractor import nlp_extractor
from app.services.matching_engine import matching_engine
from app.db.client import db_manager

router = APIRouter(prefix="/resumes", tags=["Resume Upload & Document Processing"])

@router.post("/upload")
async def upload_resumes(
    files: List[UploadFile] = File(...),
    job_id: Optional[str] = Form(None)
):
    """
    Accepts one or more CV files (PDF, DOCX, TXT), extracts text, parses candidate entities,
    stores candidate in the database, and optionally scores against a job opening.
    """
    processed_results = []
    job = None
    if job_id:
        job = db_manager.jobs.find_one({"id": job_id}) or db_manager.jobs.find_one({"_id": job_id})

    for file in files:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            processed_results.append({
                "filename": file.filename,
                "status": "error",
                "message": f"Unsupported extension {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            })
            continue

        try:
            # Generate unique filename to avoid overwrites
            unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
            save_path = UPLOAD_DIR / unique_filename

            # Save uploaded stream to disk
            with open(save_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # 1. Document Processing: Extract cleaned text
            doc_data = document_parser.extract_document(str(save_path))
            raw_text = doc_data["text"]

            if not raw_text.strip():
                processed_results.append({
                    "filename": file.filename,
                    "status": "warning",
                    "message": "Document parsed but yielded empty text (may be a scanned image)."
                })
                continue

            # 2. NLP Processing: Extract profile entities
            extracted_profile = nlp_extractor.extract_profile(raw_text, filename=file.filename)

            # 3. Database Insertion
            candidate_id = str(uuid.uuid4())
            candidate_doc = {
                "id": candidate_id,
                "name": extracted_profile["name"],
                "email": extracted_profile["email"],
                "phone": extracted_profile["phone"],
                "skills": extracted_profile["skills"],
                "experience_years": extracted_profile["experience_years"],
                "education": extracted_profile["education"],
                "education_level": extracted_profile["education_level"],
                "summary": extracted_profile["summary"],
                "raw_text": raw_text,
                "resume_filename": file.filename,
                "resume_path": str(save_path),
                "uploaded_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                "status": "Active"
            }
            db_manager.candidates.insert_one(candidate_doc)

            match_data = None
            if job:
                # 4. ML Candidate Matching if job_id provided
                match_breakdown = matching_engine.match_candidate_to_job(job, candidate_doc)
                match_data = match_breakdown.model_dump()

            db_manager.log_activity(
                "Upload Resume",
                f"Parsed and indexed candidate '{candidate_doc['name']}' from '{file.filename}'",
                "resume"
            )

            processed_results.append({
                "candidate_id": candidate_id,
                "filename": file.filename,
                "status": "success",
                "name": candidate_doc["name"],
                "skills_count": len(candidate_doc["skills"]),
                "skills": candidate_doc["skills"][:8],
                "experience_years": candidate_doc["experience_years"],
                "education": candidate_doc["education"],
                "word_count": doc_data["word_count"],
                "match": match_data
            })

        except Exception as e:
            processed_results.append({
                "filename": file.filename,
                "status": "error",
                "message": str(e)
            })

    return {
        "total_files": len(files),
        "successful": sum(1 for r in processed_results if r.get("status") == "success"),
        "results": processed_results
    }

@router.post("/upload-sample/{filename}")
def process_sample_resume(filename: str, job_id: Optional[str] = None):
    """Parses a sample resume stored on the server for instant evaluation."""
    from app.config import SAMPLE_DIR
    sample_path = SAMPLE_DIR / filename
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail=f"Sample file {filename} not found in {SAMPLE_DIR}")

    doc_data = document_parser.extract_document(str(sample_path))
    raw_text = doc_data["text"]
    extracted_profile = nlp_extractor.extract_profile(raw_text, filename=filename)

    candidate_id = str(uuid.uuid4())
    candidate_doc = {
        "id": candidate_id,
        "name": extracted_profile["name"],
        "email": extracted_profile["email"],
        "phone": extracted_profile["phone"],
        "skills": extracted_profile["skills"],
        "experience_years": extracted_profile["experience_years"],
        "education": extracted_profile["education"],
        "education_level": extracted_profile["education_level"],
        "summary": extracted_profile["summary"],
        "raw_text": raw_text,
        "resume_filename": filename,
        "resume_path": str(sample_path),
        "uploaded_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
        "status": "Active"
    }
    db_manager.candidates.insert_one(candidate_doc)

    match_data = None
    if job_id:
        job = db_manager.jobs.find_one({"id": job_id}) or db_manager.jobs.find_one({"_id": job_id})
        if job:
            match_data = matching_engine.match_candidate_to_job(job, candidate_doc).model_dump()

    db_manager.log_activity("Upload Sample", f"Parsed sample CV '{filename}' for '{candidate_doc['name']}'", "resume")

    return {
        "candidate_id": candidate_id,
        "filename": filename,
        "status": "success",
        "name": candidate_doc["name"],
        "skills_count": len(candidate_doc["skills"]),
        "skills": candidate_doc["skills"][:8],
        "experience_years": candidate_doc["experience_years"],
        "education": candidate_doc["education"],
        "word_count": doc_data["word_count"],
        "match": match_data
    }

