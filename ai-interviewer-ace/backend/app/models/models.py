"""
Base database models for the HireGage application
"""
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
import datetime

# Create a base class for all models
Base = declarative_base()

class Interview(Base):
    """Model for storing interview sessions"""
    __tablename__ = "interviews"
    
    id = Column(String, primary_key=True, index=True)  # UUID
    job_title = Column(String, nullable=False)
    company_name = Column(String, nullable=True)
    job_description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed = Column(Boolean, default=False)
    duration_minutes = Column(Integer, default=15)
    
    # Relationship with messages
    messages = relationship("Message", back_populates="interview", cascade="all, delete-orphan")
    
    # Relationship with evaluation
    evaluation = relationship("Evaluation", back_populates="interview", uselist=False, cascade="all, delete-orphan")


class Message(Base):
    """Model for storing interview messages/exchanges"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(String, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # "agent" or "candidate"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationship with interview
    interview = relationship("Interview", back_populates="messages")


class Evaluation(Base):
    """Model for storing interview evaluations"""
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(String, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, unique=True)
    summary = Column(JSON, nullable=True)
    scores = Column(JSON, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationship with interview
    interview = relationship("Interview", back_populates="evaluation")
