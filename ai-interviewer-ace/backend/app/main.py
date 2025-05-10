"""
Main application entry point for the HireGage AI Interview Agent.
This module initializes the FastAPI application and ties together all components.
"""
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any
import time
import uuid

from app.config import get_settings
from app.schemas.schemas import (
    JobTitleRequest,
    CandidateResponse,
    AgentMessage,
    InterviewResponse,
    InterviewSummary,
)
from app.agent_logic import InterviewAgent

from app.routers import api_router
from app.middleware import (
    RequestLoggingMiddleware,
    validation_exception_handler,
    hiregage_exception_handler,
    general_exception_handler
)
from app.utils.errors import HireGageError

# Configure logging
logging.basicConfig(
    level=logging.INFO if get_settings().DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("hiregage")

active_sessions: Dict[str, Dict[str, Any]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting HireGage API Server...")
    # Load models, initialize services, etc.
    yield
    # Shutdown 
    print("Shutting down HireGage API Server...")
    # Cleanup resources, close connections


app = FastAPI(
    title=get_settings().PROJECT_NAME,
    description="API for AI-powered HR interview agent",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )


# Routes
@app.get("/")
async def root():
    return {
        "message": "Welcome to HireGage AI HR Interview Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": time.time(),
        "environment": "development" if get_settings().DEBUG else "production"
    }


@app.post("/api/interview/start", response_model=InterviewResponse)
async def start_interview(request: JobTitleRequest):
    """Start a new interview session with the AI agent."""
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create a new interview agent
        interview_agent = InterviewAgent(
            job_title=request.job_title,
            company_name=request.company_name,
            job_description=request.job_description,
            interview_duration=request.interview_duration
        )
        
        # Initialize the interview
        initial_message = await interview_agent.initialize_interview()
        
        # Store the agent in active sessions
        active_sessions[session_id] = {
            "agent": interview_agent,
            "start_time": time.time(),
            "job_title": request.job_title,
            "transcript": []
        }
        
        return InterviewResponse(
            session_id=session_id,
            message=initial_message
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start interview: {str(e)}"
        )


@app.post("/api/interview/{session_id}/respond")
async def process_candidate_response(
    session_id: str,
    response: CandidateResponse
):
    """Process candidate's response and get the agent's next question."""
    if session_id not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )
    
    try:
        # Get the interview agent
        interview_session = active_sessions[session_id]
        interview_agent = interview_session["agent"]
        
        # Add candidate's response to transcript
        interview_session["transcript"].append({
            "role": "candidate",
            "content": response.text,
            "timestamp": time.time()
        })
        
        # If this is just an interim transcription update (not final), don't process it
        if not response.is_final:
            return {"status": "received"}
        
        # Get agent's response to candidate
        agent_response = await interview_agent.process_candidate_response(response.text)
        
        # Add agent's response to transcript
        interview_session["transcript"].append({
            "role": "agent",
            "content": agent_response,
            "timestamp": time.time()
        })
        
        return AgentMessage(text=agent_response)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process response: {str(e)}"
        )


@app.post("/api/interview/{session_id}/end", response_model=InterviewSummary)
async def end_interview(session_id: str):
    """End the interview and generate summary and evaluation."""
    if session_id not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )
    
    try:
        # Get the interview session
        interview_session = active_sessions[session_id]
        interview_agent = interview_session["agent"]
        
        # Generate summary and evaluation
        summary, evaluation, feedback = await interview_agent.generate_interview_summary()
        
        # Create response
        result = InterviewSummary(
            session_id=session_id,
            job_title=interview_session["job_title"],
            summary=summary,
            transcript=interview_session["transcript"],
            evaluation=evaluation,
            feedback=feedback
        )
        
        # Clean up the session (optional, can keep for history)
        # del active_sessions[session_id]
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end interview: {str(e)}"
        )


# Development testing endpoint - remove in production
if get_settings().DEBUG:
    @app.get("/api/debug/env")
    async def debug_env():
        return {
            "api_url": get_settings().API_V1_STR,
            "project_name": get_settings().PROJECT_NAME,
            "debug": get_settings().DEBUG,
            "cors_origins": get_settings().CORS_ORIGINS,
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)