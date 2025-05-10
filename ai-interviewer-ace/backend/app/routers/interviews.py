"""
API router for interview endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body,WebSocket
from typing import Dict, Any, Optional
import uuid
import time

from app.utils.tts import text_to_opus_google

from app.Agent.index import stream_graph_updates
from app.schemas import (
    JobTitleRequest, 
    InterviewResponse, 
    CandidateResponse, 
    AgentMessage,
    InterviewSummary
)
from app.utils.errors import AIServiceError

router = APIRouter(
    prefix="/interview",
    tags=["interview"],
    responses={404: {"description": "Not found"}},
)

# Store active interview sessions
active_sessions: Dict[str, Dict[str, Any]] = {}


@router.post("/start", response_model=InterviewResponse)
async def start_interview(request: JobTitleRequest):
    """
    Start a new interview session with the AI agent.
    
    - Creates a new interview session with unique ID
    - Initializes the interview agent with job details
    - Returns initial greeting and first question
    """
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
        raise AIServiceError(f"Failed to start interview: {str(e)}", e)


@router.post("/{session_id}/respond")
async def process_candidate_response(
    session_id: str,
    response: CandidateResponse
):
    """
    Process candidate's response and get the agent's next question.
    
    - Takes candidate's response (can be partial/interim or final)
    - If final, processes it and generates agent's next question
    - Updates interview transcript
    """
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
        raise AIServiceError(f"Failed to process response: {str(e)}", e)


@router.post("/{session_id}/end", response_model=InterviewSummary)
async def end_interview(session_id: str):
    """
    End the interview and generate summary and evaluation.
    
    - Completes the interview session
    - Generates summary of discussion points
    - Creates evaluation of candidate's performance
    - Provides overall feedback
    """
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
        raise AIServiceError(f"Failed to end interview: {str(e)}", e)

@router.websocket("/ws/{session_id}")
async def interview(websocket: WebSocket):
    await websocket.accept()
    user_input = ""
    while True:
        data = stream_graph_updates(user_input)
        audio_response = text_to_opus_google(data)
        await websocket.send_bytes(audio_response)
        time.sleep(60)
        user_input = await websocket.receive_text()