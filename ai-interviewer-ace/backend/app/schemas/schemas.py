"""
Pydantic schemas for API request/response validation and documentation.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import datetime


class JobTitleRequest(BaseModel):
    """Schema for starting a new interview"""
    job_title: str = Field(..., description="Job title for the interview")
    company_name: Optional[str] = Field(None, description="Company name")
    job_description: Optional[str] = Field(None, description="Detailed job description")
    interview_duration: Optional[int] = Field(15, description="Interview duration in minutes")


class CandidateResponse(BaseModel):
    """Schema for candidate's response during interview"""
    text: str = Field(..., description="Candidate's spoken response")
    is_final: bool = Field(False, description="Whether this is the final version of this response")


class AgentMessage(BaseModel):
    """Schema for agent responses"""
    text: str = Field(..., description="Agent's message text")
    type: str = Field("text", description="Message type (text, thinking, error)")


class Message(BaseModel):
    """Schema for an interview message"""
    role: str
    content: str
    timestamp: float

    class Config:
        orm_mode = True


class InterviewResponse(BaseModel):
    """Schema for interview initiation response"""
    session_id: str = Field(..., description="Unique interview session ID")
    message: str = Field(..., description="Initial agent message")


class EvaluationScore(BaseModel):
    """Schema for evaluation scores"""
    technical_skills: int = Field(..., ge=1, le=10)
    communication: int = Field(..., ge=1, le=10)
    culture_fit: int = Field(..., ge=1, le=10)
    problem_solving: int = Field(..., ge=1, le=10)
    overall_impression: int = Field(..., ge=1, le=10)


class InterviewSummary(BaseModel):
    """Schema for interview summary response"""
    session_id: str
    job_title: str
    summary: Dict[str, Any]
    transcript: List[Dict[str, str]]
    evaluation: Dict[str, Any]
    feedback: str

    class Config:
        orm_mode = True
