"""
chat.py - AI chat routes for CrimeVision AI
Allows users to ask questions about case evidence via an AI assistant.
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import Case, Evidence, ChatMessage
from app.services import groq_service

router = APIRouter(prefix="/api", tags=["Chat"])


# ---------- Request Schema ----------

class ChatRequest(BaseModel):
    """Schema for a chat message from the user"""
    message: str


# ---------- Routes ----------

@router.post("/cases/{case_id}/chat")
def chat_with_case(case_id: int, data: ChatRequest, db: Session = Depends(get_db)):
    """
    Send a message to the AI assistant about a case.
    The assistant uses all analyzed evidence as context.
    """
    # Check that the case exists
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Gather all evidence analysis results for this case
    evidence_list = db.query(Evidence).filter(Evidence.case_id == case_id).all()
    evidence_data = []
    for e in evidence_list:
        if e.analysis_result:
            try:
                analysis = json.loads(e.analysis_result)
                evidence_data.append({
                    "evidence_id": e.id,
                    "filename": e.filename,
                    "file_type": e.file_type,
                    "analysis": analysis,
                })
            except json.JSONDecodeError:
                pass  # Skip evidence with invalid JSON

    # Get chat history for context
    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.case_id == case_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    chat_history = [{"role": msg.role, "message": msg.message} for msg in history]

    # Get AI response from Groq
    assistant_response = groq_service.chat_about_case(
        evidence_data=evidence_data,
        chat_history=chat_history,
        user_message=data.message,
    )

    # Save the user message to the database
    user_msg = ChatMessage(case_id=case_id, role="user", message=data.message)
    db.add(user_msg)

    # Save the assistant response to the database
    assistant_msg = ChatMessage(case_id=case_id, role="assistant", message=assistant_response)
    db.add(assistant_msg)

    db.commit()

    return {
        "role": "assistant",
        "message": assistant_response,
    }


@router.get("/cases/{case_id}/chat")
def get_chat_history(case_id: int, db: Session = Depends(get_db)):
    """Get all chat messages for a case, ordered by time"""
    # Check that the case exists
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.case_id == case_id)
        .order_by(ChatMessage.created_at)
        .all()
    )

    return [
        {
            "id": msg.id,
            "case_id": msg.case_id,
            "role": msg.role,
            "message": msg.message,
            "created_at": str(msg.created_at),
        }
        for msg in messages
    ]
