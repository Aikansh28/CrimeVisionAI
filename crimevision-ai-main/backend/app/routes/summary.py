"""
summary.py - Case summary route for CrimeVision AI
Generates an AI-powered summary of all evidence in a case.
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Case, Evidence
from app.services import groq_service

router = APIRouter(prefix="/api", tags=["Summary"])


@router.get("/cases/{case_id}/summary")
def get_case_summary(case_id: int, db: Session = Depends(get_db)):
    """
    Generate an AI-powered summary of all analyzed evidence for a case.
    Calls Groq to synthesize a forensic case summary.
    """
    # Check that the case exists
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Build case info dict
    case_info = {
        "case_number": case.case_number,
        "case_name": case.case_name,
        "description": case.description,
        "created_at": str(case.created_at),
    }

    # Gather all evidence analyses
    evidence_list = db.query(Evidence).filter(Evidence.case_id == case_id).all()
    evidence_analyses = []
    for e in evidence_list:
        if e.analysis_result:
            try:
                analysis = json.loads(e.analysis_result)
                evidence_analyses.append({
                    "evidence_id": e.id,
                    "filename": e.filename,
                    "file_type": e.file_type,
                    "analysis": analysis,
                })
            except json.JSONDecodeError:
                pass  # Skip evidence with invalid JSON

    if not evidence_analyses:
        return {
            "case_id": case_id,
            "summary": {
                "overview": "No analyzed evidence available for this case.",
                "key_observations": [],
                "evidence_summary": [],
                "uncertainties": ["No evidence has been analyzed yet."],
            },
        }

    # Generate summary using Groq
    summary = groq_service.generate_summary(case_info, evidence_analyses)

    return {"case_id": case_id, "summary": summary}
