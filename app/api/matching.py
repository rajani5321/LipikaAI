from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import JobMatchResponse, JobResponse, CandidateMatchResult, CandidateResponse
from app.services.matching_engine import matching_engine
from app.db.client import db_manager

router = APIRouter(prefix="/matching", tags=["Candidate Matching Engine"])

@router.get("/job/{job_id}", response_model=JobMatchResponse)
def match_candidates_for_job(
    job_id: str,
    min_score: float = Query(0.0, ge=0.0, le=100.0)
):
    """
    Ranks all available candidates against a specific job vacancy using
    TF-IDF semantic similarity, skills overlap, and experience scoring.
    """
    job = db_manager.jobs.find_one({"id": job_id})
    if not job:
        job = db_manager.jobs.find_one({"_id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job vacancy not found")

    candidates = db_manager.candidates.find({})
    if not candidates:
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
            candidate_count=0
        )
        return JobMatchResponse(job=job_resp, total_candidates=0, ranked_candidates=[])

    ranked = matching_engine.rank_candidates_for_job(job, candidates)

    # Filter by minimum score if specified
    if min_score > 0.0:
        ranked = [r for r in ranked if r.match.overall_score >= min_score]

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
        candidate_count=len(candidates)
    )

    return JobMatchResponse(
        job=job_resp,
        total_candidates=len(candidates),
        ranked_candidates=ranked
    )

@router.get("/job/{job_id}/candidate/{candidate_id}", response_model=CandidateMatchResult)
def match_single_candidate(job_id: str, candidate_id: str):
    job = db_manager.jobs.find_one({"id": job_id}) or db_manager.jobs.find_one({"_id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    cand = db_manager.candidates.find_one({"id": candidate_id}) or db_manager.candidates.find_one({"_id": candidate_id})
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")

    breakdown = matching_engine.match_candidate_to_job(job, cand)
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

    return CandidateMatchResult(
        candidate=cand_resp,
        match=breakdown
    )

@router.get("/job/{job_id}/candidate/{candidate_id}/questions")
def generate_interview_questions(job_id: str, candidate_id: str):
    """Generates tailored interview questions based on candidate profile and job requirements."""
    job = db_manager.jobs.find_one({"id": job_id}) or db_manager.jobs.find_one({"_id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    cand = db_manager.candidates.find_one({"id": candidate_id}) or db_manager.candidates.find_one({"_id": candidate_id})
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")

    breakdown = matching_engine.match_candidate_to_job(job, cand)
    matched = breakdown.matched_required_skills
    missing = breakdown.missing_required_skills
    exp = float(cand.get("experience_years", 0.0))
    job_title = job.get("title", "this position")

    questions = []

    # 1. Strengths questions
    if matched:
        primary_skill = matched[0]
        secondary_skill = matched[1] if len(matched) > 1 else primary_skill
        questions.append({
            "category": "Technical Mastery",
            "tag": primary_skill,
            "question": f"Your resume highlights strong expertise in {primary_skill}. Could you describe a challenging production scenario where you leveraged {primary_skill} to solve a bottleneck or complex architecture requirement?",
            "eval_guide": f"Assess depth in {primary_skill}, error handling, scalability, and code structure."
        })
        if secondary_skill != primary_skill:
            questions.append({
                "category": "Integration & Frameworks",
                "tag": secondary_skill,
                "question": f"How do you approach testing, error monitoring, and performance profiling when building services using {secondary_skill}?",
                "eval_guide": "Look for unit testing habits, CI/CD integration, and debugging methodology."
            })

    # 2. Missing Skills / Skill Gaps questions
    if missing:
        missing_skill = missing[0]
        questions.append({
            "category": "Skill Gap Evaluation",
            "tag": f"Missing: {missing_skill}",
            "question": f"The {job_title} role requires hands-on experience with {missing_skill}, which wasn't prominently featured in your CV. Have you worked with {missing_skill} or related tooling in personal projects or past positions, and how quickly can you ramp up?",
            "eval_guide": f"Gauge learning curve, transferable skills, and conceptual foundation in {missing_skill}."
        })
        if len(missing) > 1:
            second_missing = missing[1]
            questions.append({
                "category": "Competency Transition",
                "tag": f"Missing: {second_missing}",
                "question": f"If tasked with adopting {second_missing} for our infrastructure/stack next month, what would your step-by-step approach be to integrate and ensure reliability?",
                "eval_guide": "Evaluate self-directed learning, documentation reading, and safety checks."
            })

    # 3. Experience & Architecture question
    if exp >= 3.0:
        questions.append({
            "category": "System Design & Leadership",
            "tag": "Architecture",
            "question": f"With {exp} years of industry experience, how do you handle technical debt, database query optimization, and code review standards across a sprint?",
            "eval_guide": "Evaluate architectural maturity, mentorship, and clean code principles."
        })
    else:
        questions.append({
            "category": "Engineering Growth",
            "tag": "Execution",
            "question": "Walk us through your workflow when you receive an ambiguous feature specification or encounter an unexpected production bug.",
            "eval_guide": "Look for communication skills, problem decomposition, and resilience."
        })

    # 4. Behavioral question
    questions.append({
        "category": "Teamwork & Culture",
        "tag": "Collaboration",
        "question": f"Tell us about a time when you and another developer or product manager had differing opinions on an implementation approach for {job.get('department', 'engineering')}. How was it resolved?",
        "eval_guide": "Check for empathy, data-driven reasoning, and collaboration under deadlines."
    })

    return {
        "candidate_name": cand.get("name", "Candidate"),
        "job_title": job.get("title", ""),
        "overall_score": breakdown.overall_score,
        "questions": questions
    }

