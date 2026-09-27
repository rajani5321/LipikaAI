"""
Vercel serverless entry point for LipikaAI ATS (FastAPI).
Vercel Python runtime expects the ASGI app to be importable as `app`
from the file matched by the build source.
"""
import sys
import os
from pathlib import Path

# Make the project root importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Import the FastAPI app
from app.main import app  # noqa: E402 — must be after sys.path modification
