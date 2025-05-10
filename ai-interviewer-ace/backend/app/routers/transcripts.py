"""
API router for transcript endpoints
"""
from fastapi import APIRouter, Body, HTTPException, status
from typing import Dict, Any, List
import json
import os
from datetime import datetime
import logging
from pathlib import Path

router = APIRouter(
    prefix="/transcript",
    tags=["transcript"],
    responses={404: {"description": "Not found"}},
)

# Setup logging
logger = logging.getLogger("hiregage.transcript")

# Directory to store transcript files
TRANSCRIPT_DIR = os.environ.get("TRANSCRIPT_DIR", "transcripts")

# Ensure transcript directory exists
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)


@router.post("/{session_id}/save", status_code=status.HTTP_201_CREATED)
async def save_transcript(
    session_id: str,
    data: Dict[str, Any] = Body(...)
):
    """
    Save a transcript entry to a JSON file.
    
    - Accepts transcript text and metadata
    - Appends to an existing session file or creates a new one
    - Returns success status
    """
    try:
        text = data.get("text")
        speaker = data.get("speaker")
        timestamp = data.get("timestamp", datetime.now().isoformat())
        
        if not text or not speaker:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields: text and speaker"
            )
            
        # Create session-specific transcript file
        file_path = Path(TRANSCRIPT_DIR) / f"{session_id}.json"
        
        # Prepare the transcript entry
        transcript_entry = {
            "text": text,
            "speaker": speaker,
            "timestamp": timestamp
        }
        
        # Read existing transcript or create new list
        try:
            if file_path.exists():
                with open(file_path, "r") as f:
                    transcript_data = json.load(f)
            else:
                transcript_data = []
        except json.JSONDecodeError:
            # Handle case where file exists but is not valid JSON
            transcript_data = []
            
        # Append new entry
        transcript_data.append(transcript_entry)
        
        # Write back to file
        with open(file_path, "w") as f:
            json.dump(transcript_data, f, indent=2)
            
        return {"status": "success", "message": "Transcript saved"}
    
    except Exception as e:
        logger.error(f"Error saving transcript: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save transcript: {str(e)}"
        )


@router.get("/{session_id}", response_model=List[Dict[str, Any]])
async def get_transcripts(session_id: str):
    """
    Get all transcripts for a session.
    
    - Retrieves the complete transcript history for a session
    - Returns chronologically ordered transcript entries
    """
    try:
        file_path = Path(TRANSCRIPT_DIR) / f"{session_id}.json"
        
        if not file_path.exists():
            return []
            
        with open(file_path, "r") as f:
            transcript_data = json.load(f)
            
        return transcript_data
    
    except Exception as e:
        logger.error(f"Error fetching transcripts: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch transcripts: {str(e)}"
        )


@router.get("/{session_id}/consolidated", response_model=Dict[str, Any])
async def get_consolidated_transcript(session_id: str):
    """
    Get a consolidated transcript for a session in a format suitable for model input.
    
    - Retrieves all transcript entries for a session
    - Groups responses by questions
    - Only includes interviewee responses (non-AI speaker)
    - Returns all answers grouped by questions for the model
    """
    try:
        file_path = Path(TRANSCRIPT_DIR) / f"{session_id}.json"
        
        if not file_path.exists():
            return {"final_answer": "", "raw_segments": [], "answers_by_question": []}
            
        with open(file_path, "r") as f:
            transcript_data = json.load(f)
        
        # Filter user and AI responses
        user_segments = [entry for entry in transcript_data 
                        if entry.get("speaker", "").lower() != "ai" 
                        and entry.get("text")]
        
        ai_segments = [entry for entry in transcript_data
                      if entry.get("speaker", "").lower() == "ai"
                      and entry.get("text")]
        
        # Group answers by questions
        answers_by_question = []
        
        # First, capture the most recent answer
        final_answer = user_segments[-1]["text"] if user_segments else ""
        
        # Then build the Q&A pairs
        current_question = None
        current_answers = []
        
        # Process all transcript entries chronologically
        all_segments = sorted(transcript_data, key=lambda x: x.get("timestamp", ""))
        
        for entry in all_segments:
            speaker = entry.get("speaker", "").lower()
            text = entry.get("text", "")
            
            if not text:
                continue
                
            if speaker == "ai":
                # When we encounter an AI message, it's a new question
                # Save previous Q&A pair if it exists
                if current_question and current_answers:
                    answers_by_question.append({
                        "question": current_question,
                        "answer": " ".join(current_answers)
                    })
                
                # Start a new question
                current_question = text
                current_answers = []
            else:
                # User response - add to current answer set
                if current_question:  # Only add if we have a question
                    current_answers.append(text)
        
        # Don't forget the last Q&A pair
        if current_question and current_answers:
            answers_by_question.append({
                "question": current_question,
                "answer": " ".join(current_answers)
            })
        
        # Also include all raw segments for context or analysis
        return {
            "final_answer": final_answer,
            "raw_segments": user_segments,
            "complete_transcript": " ".join([segment["text"] for segment in user_segments]),
            "answers_by_question": answers_by_question
        }
    
    except Exception as e:
        logger.error(f"Error consolidating transcripts: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to consolidate transcripts: {str(e)}"
        )
