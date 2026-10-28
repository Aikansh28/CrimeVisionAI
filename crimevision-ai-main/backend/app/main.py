"""
main.py - Entry point for the CrimeVision AI API
Sets up FastAPI app, CORS, routers, and database tables.
"""

import sys
import os

# Ensure the backend directory is in Python's import search path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base
from app.routes import cases, evidence, chat, report, timeline, summary

# Create the FastAPI application
app = FastAPI(title="CrimeVision AI API")

# --- CORS Middleware (allow all origins for development) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include all route modules ---
app.include_router(cases.router)
app.include_router(evidence.router)
app.include_router(chat.router)
app.include_router(report.router)
app.include_router(timeline.router)
app.include_router(summary.router)

# --- Create database tables on startup ---
Base.metadata.create_all(bind=engine)

# --- Mount the uploads directory as static files ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# --- Root endpoint ---
@app.get("/")
def root():
    """Health check endpoint"""
    return {"message": "CrimeVision AI API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
