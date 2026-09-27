from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# ----------------- User & Auth Schemas -----------------
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    name: str
    role: str = "Lead Technical Recruiter"
    department: str = "Human Resources"
    email: Optional[str] = ""

class UserResponse(BaseModel):
    id: str
    username: str
    name: str
    role: str
    department: str
    email: Optional[str] = ""

# ----------------- Job Schemas -----------------
class JobCreate(BaseModel):
    title: str = Field(..., example="Senior Python Developer")
    department: str = Field(default="Engineering", example="Backend Engineering")
    required_skills: List[str] = Field(..., example=["Python", "Django", "FastAPI", "SQL", "REST API"])
    preferred_skills: List[str] = Field(default=[], example=["Docker", "AWS", "Redis"])
    min_experience: float = Field(default=2.0, ge=0.0, example=2.0)
    education_level: str = Field(default="Bachelor", example="Bachelor in Computer Science or related")
    description: str = Field(..., example="We are looking for an experienced Python developer to build robust APIs...")
    status: str = Field(default="Active", example="Active")

class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    min_experience: Optional[float] = None
    education_level: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class JobResponse(BaseModel):
    id: str
    title: str
    department: str
    required_skills: List[str]
    preferred_skills: List[str]
    min_experience: float
    education_level: str
    description: str
    status: str
    created_at: str
    candidate_count: Optional[int] = 0

# ----------------- Candidate Schemas -----------------
class CandidateCreate(BaseModel):
    name: str
    email: Optional[str] = ""
    phone: Optional[str] = ""
    skills: List[str] = []
    experience_years: float = 0.0
    education: Optional[str] = "Not Specified"
    summary: Optional[str] = ""
    raw_text: Optional[str] = ""
    resume_filename: Optional[str] = ""
    resume_path: Optional[str] = ""

class CandidateResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    skills: List[str]
    experience_years: float
    education: str
    summary: str
    raw_text: str
    resume_filename: str
    resume_path: str
    uploaded_at: str
    status: str = "Active"  # Active, Shortlisted, Interviewed, Rejected

class CandidateStatusUpdate(BaseModel):
    status: str

# ----------------- Matching & Explainability Schemas -----------------
class MatchBreakdown(BaseModel):
    overall_score: float         # 0 - 100%
    skill_score: float           # 0 - 100%
    semantic_score: float        # 0 - 100%
    experience_score: float      # 0 - 100%
    education_score: float       # 0 - 100%
    matched_required_skills: List[str]
    matched_preferred_skills: List[str]
    missing_required_skills: List[str]
    extra_skills: List[str]
    recommendation: str          # "Strong Match", "Good Match", "Moderate Match", "Low Match"
    verdict: str                 # Human-readable summary for HR

class CandidateMatchResult(BaseModel):
    candidate: CandidateResponse
    match: MatchBreakdown

class JobMatchResponse(BaseModel):
    job: JobResponse
    total_candidates: int
    ranked_candidates: List[CandidateMatchResult]

# ----------------- Comparison Schemas -----------------
class CompareRequest(BaseModel):
    job_id: str
    candidate_ids: List[str]

class CandidateComparisonItem(BaseModel):
    candidate: CandidateResponse
    match: MatchBreakdown
    strengths: List[str]
    gaps: List[str]

class CompareResult(BaseModel):
    job: JobResponse
    candidates: List[CandidateComparisonItem]
    top_candidate_id: str
    hr_recommendation_summary: str

# ----------------- Analytics & Overview -----------------
class AnalyticsOverview(BaseModel):
    total_jobs: int
    active_jobs: int
    total_candidates: int
    total_cvs_uploaded: int
    average_match_score: float
    high_match_candidates: int
    top_skills_in_demand: Dict[str, int]
    score_distribution: Dict[str, int]
    recent_activity: List[Dict[str, Any]]
