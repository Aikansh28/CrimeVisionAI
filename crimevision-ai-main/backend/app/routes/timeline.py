"""
timeline.py - Timeline generation route for CrimeVision AI
Extracts time-based events from analyzed evidence.
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Case, Evidence

router = APIRouter(prefix="/api", tags=["Timeline"])


@router.get("/cases/{case_id}/timeline")
def get_timeline(case_id: int, db: Session = Depends(get_db)):
    """
    Build a timeline from all analyzed evidence.
    Extracts time mentions and events from each evidence's analysis_result.
    """
    # Check that the case exists
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Get all evidence with analysis results
    evidence_list = (
        db.query(Evidence)
        .filter(Evidence.case_id == case_id)
        .order_by(Evidence.created_at)
        .all()
    )

    timeline = []

    for e in evidence_list:
        if not e.analysis_result:
            continue  # Skip un-analyzed evidence

        try:
            analysis = json.loads(e.analysis_result)
        except json.JSONDecodeError:
            continue

        if e.file_type == "image":
            # Extract observations from image analysis
            scene = analysis.get("scene", "")
            observations = analysis.get("observations", [])

            # Add the scene as a timeline entry
            if scene:
                evt_text = f"Scene observed: {scene[:200]}"
                timeline.append({
                    "time": "Time unavailable",
                    "event": evt_text,
                    "description": evt_text,
                    "source": "Image",
                    "evidence_id": e.id,
                })

            # Add each observation as a timeline entry
            for obs in observations:
                # Try to extract any time reference from the observation
                time_str = "Time unavailable"
                obs_lower = obs.lower()
                # Simple heuristic: look for common time patterns
                for keyword in ["pm", "am", "o'clock", "timestamp", "approximately"]:
                    if keyword in obs_lower:
                        time_str = obs
                        break

                timeline.append({
                    "time": time_str,
                    "event": obs,
                    "description": obs,
                    "source": "Image",
                    "evidence_id": e.id,
                })

        elif e.file_type == "audio":
            # Extract key_events from audio/transcript analysis
            key_events = analysis.get("key_events", [])

            for event in key_events:
                # key_events can be dicts with "time" and "event" keys, or strings
                if isinstance(event, dict):
                    evt_name = event.get("event") or event.get("description") or "Unknown event"
                    timeline.append({
                        "time": event.get("time", "Time unavailable"),
                        "event": evt_name,
                        "description": evt_name,
                        "source": "Audio",
                        "evidence_id": e.id,
                    })
                elif isinstance(event, str):
                    timeline.append({
                        "time": "Time unavailable",
                        "event": event,
                        "description": event,
                        "source": "Audio",
                        "evidence_id": e.id,
                    })

            # Also add summary if available
            summary = analysis.get("summary", "")
            if summary:
                sum_text = f"Audio summary: {summary[:200]}"
                timeline.append({
                    "time": "Time unavailable",
                    "event": sum_text,
                    "description": sum_text,
                    "source": "Audio",
                    "evidence_id": e.id,
                })

    return {"case_id": case_id, "timeline": timeline}
