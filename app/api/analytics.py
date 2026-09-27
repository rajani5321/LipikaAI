from typing import Dict, Any, List
from collections import Counter
from fastapi import APIRouter
from app.models.schemas import AnalyticsOverview
from app.db.client import db_manager
from app.services.matching_engine import matching_engine

router = APIRouter(prefix="/analytics", tags=["HR Analytics & Metrics"])

@router.get("/dashboard", response_model=AnalyticsOverview)
def get_dashboard_metrics():
    """Aggregates high-level recruitment metrics and distribution stats for the HR dashboard."""
    jobs = db_manager.jobs.find({})
    candidates = db_manager.candidates.find({})
    
    total_jobs = len(jobs)
    active_jobs = sum(1 for j in jobs if j.get("status", "Active") == "Active")
    total_candidates = len(candidates)
    
    # Calculate skill demand
    skills_counter = Counter()
    for j in jobs:
        for s in j.get("required_skills", []):
            skills_counter[s] += 1
        for s in j.get("preferred_skills", []):
            skills_counter[s] += 1
            
    top_skills = dict(skills_counter.most_common(8))

    # Evaluate scores across the first active job or sample
    score_distribution = {
        "Strong (80-100%)": 0,
        "Good (65-79%)": 0,
        "Moderate (50-64%)": 0,
        "Low (<50%)": 0
    }
    
    all_scores = []
    if jobs and candidates:
        primary_job = next((j for j in jobs if j.get("status") == "Active"), jobs[0])
        for c in candidates:
            mb = matching_engine.match_candidate_to_job(primary_job, c)
            score = mb.overall_score
            all_scores.append(score)
            if score >= 80.0:
                score_distribution["Strong (80-100%)"] += 1
            elif score >= 65.0:
                score_distribution["Good (65-79%)"] += 1
            elif score >= 50.0:
                score_distribution["Moderate (50-64%)"] += 1
            else:
                score_distribution["Low (<50%)"] += 1

    avg_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0.0
    high_match_count = score_distribution["Strong (80-100%)"] + score_distribution["Good (65-79%)"]

    # Activity feed
    activities = db_manager.activity.find({})
    # Return last 6 activities
    activities = sorted(activities, key=lambda x: x.get("timestamp", ""), reverse=True)[:6]

    return AnalyticsOverview(
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        total_candidates=total_candidates,
        total_cvs_uploaded=total_candidates,
        average_match_score=avg_score,
        high_match_candidates=high_match_count,
        top_skills_in_demand=top_skills,
        score_distribution=score_distribution,
        recent_activity=activities
    )

@router.get("/system-status")
def get_system_status():
    """Returns database connection status, model configuration, and engine health."""
    db_status = db_manager.get_status()
    return {
        "status": "online",
        "database": db_status,
        "ml_engine": "TF-IDF + Cosine Similarity + Hierarchical Feature Normalizer",
        "doc_parsers": ["pypdf (PDF)", "python-docx (DOCX)", "PlainText (TXT)"],
        "weights": matching_engine.weights
    }
