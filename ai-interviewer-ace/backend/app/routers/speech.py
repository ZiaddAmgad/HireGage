"""
API router for speech recognition and transcription WebSocket endpoints
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, BackgroundTasks
from typing import Dict, Any, List
import asyncio
import logging
import uuid
import json
import os
from datetime import datetime
from pathlib import Path

from app.services.transcription import VoskTranscriptionService

# Initialize router
router = APIRouter(
    prefix="/speech",
    tags=["speech"],
)

# Set up logging
logger = logging.getLogger("hiregage.speech")

# Directory to store temporary audio files
TEMP_AUDIO_DIR = os.environ.get("TEMP_AUDIO_DIR", "temp_audio")
Path(TEMP_AUDIO_DIR).mkdir(exist_ok=True)

# Create transcription service instance
try:
    # The model needs to be downloaded from https://alphacephei.com/vosk/models
    # and extracted to the models directory
    transcription_service = VoskTranscriptionService()
    logger.info("Transcription service initialized")
except FileNotFoundError as e:
    logger.error(f"Error initializing transcription service: {str(e)}")
    transcription_service = None

# Track active transcription sessions
active_sessions: Dict[str, Dict[str, Any]] = {}


@router.websocket("/ws/{session_id}")
async def speech_recognition_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time speech recognition.
    
    Client sends audio chunks and receives transcription results.
    """
    if transcription_service is None:
        await websocket.close(code=1013, reason="Transcription service not available")
        return
    
    await websocket.accept()
    logger.info(f"WebSocket connection established for session {session_id}")
    
    # Create unique transcription ID for this connection
    transcription_id = str(uuid.uuid4())
    active_sessions[transcription_id] = {
        "session_id": session_id,
        "start_time": datetime.now().isoformat(),
        "transcriptions": []
    }
    
    try:
        # Process audio chunks
        async def audio_generator():
            while True:
                # Receive binary audio data from client
                data = await websocket.receive_bytes()
                if not data:
                    break
                yield data
        
        # Process and send transcription results
        async for result in transcription_service.transcribe_stream(audio_generator()):
            # Store partial/final results
            if "text" in result and result["text"]:
                active_sessions[transcription_id]["transcriptions"].append({
                    "text": result["text"],
                    "is_final": True,
                    "timestamp": datetime.now().isoformat()
                })
                await websocket.send_json({
                    "type": "transcription",
                    "text": result["text"],
                    "is_final": True
                })
            elif "partial" in result and result["partial"]:
                await websocket.send_json({
                    "type": "transcription",
                    "text": result["partial"],
                    "is_final": False
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"Error in WebSocket: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
    finally:
        # Clean up session data if needed
        if transcription_id in active_sessions:
            # Could save final transcription to database here
            del active_sessions[transcription_id]
        
        try:
            await websocket.close()
        except:
            pass


@router.post("/download-model")
async def download_model(
    background_tasks: BackgroundTasks,
    model_name: str = "vosk-model-en-us-0.22"
):
    """
    Download a Vosk model in the background.
    
    Available models: https://alphacephei.com/vosk/models
    """
    # This would handle downloading and extracting the model
    # For production use, consider a more robust implementation with progress tracking
    
    async def download_model_task(model_name: str):
        import requests
        import zipfile
        import io
        
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        model_dir = models_dir / model_name
        
        if model_dir.exists():
            logger.info(f"Model {model_name} already exists")
            return {"status": "exists", "model_name": model_name}
        
        logger.info(f"Downloading model {model_name}")
        
        try:
            url = f"https://alphacephei.com/vosk/models/{model_name}.zip"
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Extract the ZIP file
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                zip_file.extractall(str(models_dir))
            
            logger.info(f"Model {model_name} downloaded and extracted")
            return {"status": "success", "model_name": model_name}
            
        except Exception as e:
            logger.error(f"Error downloading model {model_name}: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    # Add the task to background tasks
    background_tasks.add_task(download_model_task, model_name)
    
    return {
        "message": f"Downloading model {model_name} in the background",
        "status": "started"
    }
