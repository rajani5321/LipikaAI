import re
from typing import Dict, Any, List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import MATCHING_WEIGHTS
from app.models.schemas import MatchBreakdown, CandidateMatchResult, CandidateResponse, JobResponse

class CandidateMatchingEngine:
    """Machine Learning & NLP Candidate-Job Matching Engine."""

    def __init__(self):
        self.weights = MATCHING_WEIGHTS
        # Degree level mapping
        self.edu_levels = {
            "phd": 5, "doctorate": 5,
            "master": 4, "mca": 4, "m.tech": 4, "ms": 4, "mba": 4,
            "bachelor": 3, "b.tech": 3, "bca": 3, "bs": 3, "b.e": 3,
            "diploma": 2, "high school": 1
        }

    def _get_education_level(self, text: str) -> int:
        if not text:
            return 2
        text_lower = text.lower()
        for deg, lvl in self.edu_levels.items():
            if deg in text_lower:
                return lvl
        return 3 # Default to Bachelor level if unspecified

    def calculate_semantic_similarity(self, job_text: str, resume_text: str) -> float:
        """Computes TF-IDF Cosine Similarity between Job and Resume text."""
        if not job_text.strip() or not resume_text.strip():
            return 0.0

        try:
            vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                sublinear_tf=True,
                max_features=5000
            )
            tfidf_matrix = vectorizer.fit_transform([job_text, resume_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            # Convert to percentage and bound between 0 and 100
            score = float(np.clip(similarity * 100.0, 0.0, 100.0))
            return round(score, 1)
        except Exception as e:
            print(f"[Matching Engine] TF-IDF error: {e}")
            return 50.0

    def evaluate_skills(self, job_required: List[str], job_preferred: List[str], candidate_skills: List[str]) -> Tuple[float, List[str], List[str], List[str], List[str]]:
        """Calculates skills match ratio, identifying matched and missing skills."""
        req_set = {s.strip().lower(): s.strip() for s in job_required}
        pref_set = {s.strip().lower(): s.strip() for s in (job_preferred or [])}
        cand_map = {s.strip().lower(): s.strip() for s in candidate_skills}

        matched_req = [req_set[k] for k in req_set if k in cand_map]
        missing_req = [req_set[k] for k in req_set if k not in cand_map]
        matched_pref = [pref_set[k] for k in pref_set if k in cand_map]
        
        # Extra skills possessed by candidate not in required/preferred
        all_job_skills = set(req_set.keys()).union(set(pref_set.keys()))
        extra_skills = [cand_map[k] for k in cand_map if k not in all_job_skills]

        # Calculate base score on required skills
        req_ratio = len(matched_req) / max(1, len(req_set))
        
        # Bonus for preferred skills (up to 15%)
        pref_ratio = len(matched_pref) / max(1, len(pref_set)) if pref_set else 0.0
        
        if pref_set:
            final_skill_ratio = (req_ratio * 0.85) + (pref_ratio * 0.15)
        else:
            final_skill_ratio = req_ratio

        skill_score = round(min(1.0, final_skill_ratio) * 100.0, 1)
        return skill_score, matched_req, matched_pref, missing_req, extra_skills

    def evaluate_experience(self, job_min_exp: float, candidate_exp: float) -> float:
        """Evaluates experience alignment against minimum requirements."""
        if job_min_exp <= 0:
            return 100.0
        
        if candidate_exp >= job_min_exp:
            # Full score, with small reward for seniority up to 100
            return 100.0
        else:
            # Proportional score
            ratio = candidate_exp / job_min_exp
            return round(ratio * 80.0, 1)

    def evaluate_education(self, job_edu: str, candidate_edu: str) -> float:
        """Evaluates candidate educational qualification against job requirements."""
        req_lvl = self._get_education_level(job_edu)
        cand_lvl = self._get_education_level(candidate_edu)

        if cand_lvl >= req_lvl:
            return 100.0
        elif cand_lvl == req_lvl - 1:
            return 75.0
        else:
            return 50.0

    def generate_verdict(
        self,
        overall_score: float,
        matched_req: List[str],
        missing_req: List[str],
        req_count: int,
        cand_exp: float,
        job_min_exp: float
    ) -> Tuple[str, str]:
        """Produces qualitative recommendation and plain-text HR verdict."""
        if overall_score >= 80.0:
            recommendation = "Strong Match"
        elif overall_score >= 65.0:
            recommendation = "Good Match"
        elif overall_score >= 50.0:
            recommendation = "Moderate Match"
        else:
            recommendation = "Low Match"

        skills_summary = f"Matches {len(matched_req)} of {req_count} core skills"
        if missing_req:
            missing_text = f" (Missing: {', '.join(missing_req[:3])}{'...' if len(missing_req) > 3 else ''})"
        else:
            missing_text = " (All required skills satisfied)"

        exp_text = f"Has {cand_exp} yrs exp vs {job_min_exp} yrs required."
        
        if recommendation == "Strong Match":
            action = "Highly recommended for technical interview round."
        elif recommendation == "Good Match":
            action = "Recommended for initial phone screening."
        elif recommendation == "Moderate Match":
            action = "Consider if secondary requirements can be trained."
        else:
            action = "Profile does not meet critical vacancy benchmarks."

        verdict = f"{skills_summary}{missing_text}. {exp_text} {action}"
        return recommendation, verdict

    def match_candidate_to_job(self, job: Dict[str, Any], candidate: Dict[str, Any]) -> MatchBreakdown:
        """Executes multi-factor match analysis between a candidate and a job opening."""
        # 1. Semantic Match via TF-IDF
        job_full_text = f"{job.get('title', '')} {job.get('description', '')} {' '.join(job.get('required_skills', []))}"
        cand_text = candidate.get("raw_text", "") or candidate.get("summary", "")
        semantic_score = self.calculate_semantic_similarity(job_full_text, cand_text)

        # 2. Skills Match
        req_skills = job.get("required_skills", [])
        pref_skills = job.get("preferred_skills", [])
        cand_skills = candidate.get("skills", [])
        skill_score, matched_req, matched_pref, missing_req, extra_skills = self.evaluate_skills(
            req_skills, pref_skills, cand_skills
        )

        # 3. Experience Match
        job_min_exp = float(job.get("min_experience", 0.0))
        cand_exp = float(candidate.get("experience_years", 0.0))
        exp_score = self.evaluate_experience(job_min_exp, cand_exp)

        # 4. Education Match
        edu_score = self.evaluate_education(
            job.get("education_level", "Bachelor"),
            candidate.get("education", "Bachelor")
        )

        # 5. Composite Weighted Score
        overall_score = round(
            (skill_score * self.weights["skills"]) +
            (semantic_score * self.weights["semantic"]) +
            (exp_score * self.weights["experience"]) +
            (edu_score * self.weights["education"]),
            1
        )

        recommendation, verdict = self.generate_verdict(
            overall_score,
            matched_req,
            missing_req,
            len(req_skills),
            cand_exp,
            job_min_exp
        )

        return MatchBreakdown(
            overall_score=overall_score,
            skill_score=skill_score,
            semantic_score=semantic_score,
            experience_score=exp_score,
            education_score=edu_score,
            matched_required_skills=matched_req,
            matched_preferred_skills=matched_pref,
            missing_required_skills=missing_req,
            extra_skills=extra_skills,
            recommendation=recommendation,
            verdict=verdict
        )

    def rank_candidates_for_job(self, job: Dict[str, Any], candidates: List[Dict[str, Any]]) -> List[CandidateMatchResult]:
        """Scores and ranks an entire candidate pool for a given job vacancy."""
        results = []
        for cand in candidates:
            match_breakdown = self.match_candidate_to_job(job, cand)
            
            # Format candidate response
            cand_response = CandidateResponse(
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
            
            results.append(CandidateMatchResult(
                candidate=cand_response,
                match=match_breakdown
            ))

        # Sort descending by overall match score
        results.sort(key=lambda x: x.match.overall_score, reverse=True)
        return results

matching_engine = CandidateMatchingEngine()
