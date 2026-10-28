"""
cases.py - Case management routes for CrimeVision AI
Handles creating, listing, and loading demo data for cases.
"""

import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from app.database import get_db
from app.models import Case, Evidence, ChatMessage

router = APIRouter(prefix="/api/cases", tags=["Cases"])


# ---------- Request Schemas ----------

class CaseCreate(BaseModel):
    """Schema for creating a new case - accepts either case_name or name"""
    case_name: str | None = None
    name: str | None = None
    description: str | None = None


# ---------- Helper ----------

def _generate_case_number(db: Session) -> str:
    """Generate the next case number like CV-2024-001"""
    year = datetime.utcnow().year
    # Count existing cases to determine the next sequential number
    count = db.query(Case).count()
    return f"CV-{year}-{count + 1:03d}"


# ---------- Routes ----------

@router.post("")
def create_case(data: CaseCreate, db: Session = Depends(get_db)):
    """Create a new forensic case"""
    case_number = _generate_case_number(db)
    final_name = data.case_name or data.name or "Untitled Case"

    case = Case(
        case_number=case_number,
        case_name=final_name,
        description=data.description,
    )
    db.add(case)
    db.commit()
    db.refresh(case)

    return {
        "id": case.id,
        "case_number": case.case_number,
        "case_name": case.case_name,
        "name": case.case_name,
        "description": case.description,
        "created_at": str(case.created_at),
        "evidence_count": 0,
    }


@router.get("")
def list_cases(db: Session = Depends(get_db)):
    """List all cases with their evidence count"""
    cases = db.query(Case).order_by(Case.created_at.desc()).all()

    result = []
    for case in cases:
        # Count evidence files for this case
        evidence_count = db.query(func.count(Evidence.id)).filter(
            Evidence.case_id == case.id
        ).scalar()

        result.append({
            "id": case.id,
            "case_number": case.case_number,
            "case_name": case.case_name,
            "name": case.case_name,
            "description": case.description,
            "created_at": str(case.created_at),
            "evidence_count": evidence_count,
        })

    return result


@router.get("/{case_id}")
def get_case(case_id: int, db: Session = Depends(get_db)):
    """Get a single case by ID with evidence count"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    evidence_count = db.query(func.count(Evidence.id)).filter(
        Evidence.case_id == case.id
    ).scalar()

    return {
        "id": case.id,
        "case_number": case.case_number,
        "case_name": case.case_name,
        "name": case.case_name,
        "description": case.description,
        "created_at": str(case.created_at),
        "evidence_count": evidence_count,
    }


@router.post("/{case_id}/demo")
def load_demo_data(case_id: int, db: Session = Depends(get_db)):
    """
    Load demo/fictional data into a case for testing purposes.
    Creates sample evidence entries with pre-filled analysis results.
    ALL DATA IS FICTIONAL AND FOR DEMONSTRATION ONLY.
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # --- Demo image evidence with fictional analysis ---
    image_analysis = {
        "people": [
            "One individual appears to be standing near the doorway",
            "A second person appears to be seated at a table",
        ],
        "weapons": [
            "No weapons visibly identified in the scene",
        ],
        "objects": [
            "A wooden table with scattered papers",
            "A laptop computer (appears to be open)",
            "Two coffee cups on the table",
            "A dark-colored backpack near the chair",
        ],
        "scene": (
            "The scene appears to be a dimly lit room, possibly a residential living area. "
            "There are signs of recent activity — papers are scattered, and personal belongings "
            "are visible. The lighting suggests the image was captured in the evening."
        ),
        "observations": [
            "The room appears to have been recently occupied",
            "Papers on the table may contain relevant information",
            "The backpack near the chair could contain personal belongings",
            "Timestamp on the image suggests approximately 9:45 PM",
            "[DEMO] This is fictional data for demonstration purposes",
        ],
    }

    evidence_image = Evidence(
        case_id=case_id,
        filename="demo_crime_scene.jpg",
        file_type="image",
        file_path="uploads/demo_crime_scene.jpg",
        analysis_result=json.dumps(image_analysis),
    )
    db.add(evidence_image)

    # --- Demo audio evidence with fictional transcript analysis ---
    audio_analysis = {
        "transcript": (
            "At approximately 10:15 PM, I heard loud voices coming from the apartment next door. "
            "There were two people arguing. One voice was deeper, possibly male. "
            "I heard what sounded like furniture being moved around 10:20 PM. "
            "Then it went quiet for about five minutes. After that, I heard a door slam "
            "and footsteps in the hallway at around 10:25 PM."
        ),
        "key_events": [
            {"time": "10:15 PM", "event": "Loud voices heard from adjacent apartment"},
            {"time": "10:20 PM", "event": "Sounds of furniture being moved"},
            {"time": "10:25 PM", "event": "Door slam and footsteps in hallway"},
        ],
        "witness_statements": [
            "Witness reports hearing two people arguing",
            "Witness describes one voice as deeper, possibly male",
            "Witness heard furniture movement approximately 5 minutes after arguing began",
        ],
        "important_information": [
            "The incident appears to have lasted approximately 10 minutes",
            "At least two individuals appear to have been involved",
            "Physical disturbance (furniture movement) was reported",
            "Someone appears to have left the apartment at 10:25 PM",
        ],
        "summary": (
            "A witness reports hearing a disturbance in an adjacent apartment between "
            "approximately 10:15 PM and 10:25 PM. The disturbance included raised voices, "
            "possible furniture movement, and ended with someone apparently leaving the premises."
        ),
        "_demo_note": "This is fictional data for demonstration purposes",
    }

    evidence_audio = Evidence(
        case_id=case_id,
        filename="demo_witness_recording.mp3",
        file_type="audio",
        file_path="uploads/demo_witness_recording.mp3",
        analysis_result=json.dumps(audio_analysis),
    )
    db.add(evidence_audio)

    # --- Demo chat messages ---
    demo_messages = [
        ChatMessage(
            case_id=case_id,
            role="user",
            message="What can you tell me about the people in the scene?",
        ),
        ChatMessage(
            case_id=case_id,
            role="assistant",
            message=(
                "Based on the available evidence, the image analysis indicates that two individuals "
                "appear to be present in the scene. One person appears to be standing near the "
                "doorway, while a second individual appears to be seated at a table. "
                "The witness audio recording also mentions hearing two people. "
                "Please note that no identifications can be confirmed from the evidence alone."
            ),
        ),
        ChatMessage(
            case_id=case_id,
            role="user",
            message="What is the timeline of events?",
        ),
        ChatMessage(
            case_id=case_id,
            role="assistant",
            message=(
                "Based on the analyzed evidence, here is the approximate timeline:\n\n"
                "• ~9:45 PM — Image evidence timestamp suggests the scene was photographed.\n"
                "• ~10:15 PM — Witness reports hearing loud voices from the adjacent apartment.\n"
                "• ~10:20 PM — Sounds of furniture being moved were heard.\n"
                "• ~10:25 PM — A door slam and footsteps in the hallway were reported.\n\n"
                "Note: These times are approximate and based on witness statements."
            ),
        ),
    ]
    db.add_all(demo_messages)

    db.commit()

    return {
        "message": "Demo data loaded successfully",
        "note": "ALL DATA IS FICTIONAL AND FOR DEMONSTRATION PURPOSES ONLY",
        "evidence_created": 2,
        "chat_messages_created": len(demo_messages),
    }
