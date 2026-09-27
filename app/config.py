import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
SAMPLE_DIR = DATA_DIR / "sample_resumes"
FALLBACK_DB_FILE = DATA_DIR / "db_store.json"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

# Application Meta
PROJECT_TITLE = "AI-Based HR Resume Screening & Candidate Matching System"
VERSION = "2.0.0"
DESCRIPTION = "Intelligent ATS platform combining NLP, Document Parsing, TF-IDF Semantic Matching, and MongoDB"

# Database Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "resume_screening_db")
MONGO_TIMEOUT_MS = int(os.getenv("MONGO_TIMEOUT_MS", 1500))

# Scoring Weights for Candidate Matching
MATCHING_WEIGHTS = {
    "skills": 0.45,      # 45% Skills alignment (Required + Preferred)
    "semantic": 0.30,    # 30% TF-IDF Cosine Semantic text similarity
    "experience": 0.15,  # 15% Years of relevant experience
    "education": 0.10    # 10% Qualification / Degree level match
}

# Allowed file extensions
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE_MB = 15
