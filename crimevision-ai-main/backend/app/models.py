"""
models.py - Database models for CrimeVision AI
Defines the Cases, Evidence, and ChatMessages tables.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.database import Base


class Case(Base):
    """Represents a forensic case"""
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_number = Column(String, unique=True, nullable=False)  # e.g. "CV-2024-001"
    case_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Evidence(Base):
    """Represents a piece of evidence (image or audio) linked to a case"""
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # "image" or "audio"
    file_path = Column(String, nullable=False)
    analysis_result = Column(Text, nullable=True)  # Stores JSON string
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    """Represents a chat message between user and AI assistant for a case"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
