"""
evidence.py - Evidence upload and analysis routes for CrimeVision AI
Handles file uploads and triggers AI analysis via Groq.
"""

import os
import json
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Case, Evidence
from app.services import groq_service

router = APIRouter(prefix="/api", tags=["Evidence"])

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav"}
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_AUDIO_EXTENSIONS

# Base directory of the backend
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")


@router.post("/cases/{case_id}/evidence")
async def upload_evidence(case_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload an evidence file (image or audio) for a case.
    Accepts JPG, PNG, MP3, WAV files only.
    """
    # Check that the case exists
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Validate file extension
    filename = file.filename or "unknown"
    _, extension = os.path.splitext(filename)
    extension = extension.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{extension}' not allowed. Accepted: JPG, PNG, MP3, WAV",
        )

    # Determine file type (image or audio)
    if extension in ALLOWED_IMAGE_EXTENSIONS:
        file_type = "image"
    else:
        file_type = "audio"

    # Save the uploaded file to the uploads directory
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # Use a unique filename to avoid collisions: caseId_originalName
    safe_filename = f"{case_id}_{filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create evidence record in the database
    evidence = Evidence(
        case_id=case_id,
        filename=filename,
        file_type=file_type,
        file_path=file_path,
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return {
        "id": evidence.id,
        "case_id": evidence.case_id,
        "filename": evidence.filename,
        "file_type": evidence.file_type,
        "file_path": evidence.file_path,
        "created_at": str(evidence.created_at),
    }


@router.get("/cases/{case_id}/evidence")
def list_evidence(case_id: int, db: Session = Depends(get_db)):
    """List all evidence files for a case"""
    # Check that the case exists
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    evidence_list = (
        db.query(Evidence)
        .filter(Evidence.case_id == case_id)
        .order_by(Evidence.created_at)
        .all()
    )

    result = []
    for e in evidence_list:
        result.append({
            "id": e.id,
            "case_id": e.case_id,
            "filename": e.filename,
            "file_type": e.file_type,
            "file_path": e.file_path,
            "analysis_result": json.loads(e.analysis_result) if e.analysis_result else None,
            "created_at": str(e.created_at),
        })

    return result


@router.post("/evidence/{evidence_id}/analyze")
def analyze_evidence(evidence_id: int, db: Session = Depends(get_db)):
    """
    Analyze a piece of evidence using AI.
    - Images are analyzed with Groq's vision model.
    - Audio files are transcribed then analyzed.
    """
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    if evidence.file_type == "image":
        # Analyze image directly with vision model
        result = groq_service.analyze_image(evidence.file_path)

    elif evidence.file_type == "audio":
        # First transcribe the audio, then analyze the transcript
        transcript = groq_service.transcribe_audio(evidence.file_path)
        result = groq_service.analyze_transcript(transcript)

    else:
        raise HTTPException(status_code=400, detail="Unknown evidence file type")

    # Store the analysis result as JSON in the database
    evidence.analysis_result = json.dumps(result)
    db.commit()
    db.refresh(evidence)

    return {
        "evidence_id": evidence.id,
        "file_type": evidence.file_type,
        "analysis_result": result,
    }
