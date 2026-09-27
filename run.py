import sys
import os

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import uvicorn
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.config import PROJECT_TITLE, VERSION
from app.db.client import db_manager

def main():
    import argparse
    parser = argparse.ArgumentParser(description=PROJECT_TITLE)
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", 8000)), help="Port to run server on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()

    port = args.port
    host = args.host

    print("=" * 72)
    print(f"[AI]  {PROJECT_TITLE}")
    print(f"      Version: {VERSION}")
    print("=" * 72)
    
    db_status = db_manager.get_status()
    print(f"[DB]  Database Engine: {db_status['engine']}")
    print(f"      Status: {db_status['message']}")
    print("-" * 72)
    print(f">>  HR Dashboard UI:    http://{host}:{port}")
    print(f">>  Swagger API Docs:   http://{host}:{port}/docs")
    print(f">>  ReDoc API Docs:     http://{host}:{port}/redoc")
    print("=" * 72)
    print(f">>  Starting ASGI Server (Uvicorn) on port {port}... Press Ctrl+C to stop.")
    print()

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=args.reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()
