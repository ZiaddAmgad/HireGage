"""
Speech transcription service using Vosk for offline speech recognition
"""
import os
import json
import asyncio
import logging
import numpy as np
from typing import AsyncGenerator, Optional
from pathlib import Path
from vosk import Model, KaldiRecognizer, SetLogLevel

# Set up logging
logger = logging.getLogger("hiregage.transcription")

# Set Vosk logging level (0 for debug, -1 for info, -2 for warning, -3 for error)
SetLogLevel(-1)

# Default paths for models
DEFAULT_MODEL_DIR = os.environ.get("VOSK_MODEL_DIR", "models/vosk-model-en-us-0.22")
MODELS_DIR = Path("models")

class VoskTranscriptionService:
    """Vosk-based speech transcription service"""
    
    def __init__(self, model_path: Optional[str] = None, sample_rate: int = 16000):
        """
        Initialize the Vosk transcription service
        
        Args:
            model_path: Path to the Vosk model directory (optional)
            sample_rate: Audio sample rate in Hz (default: 16000)
        """
        self.sample_rate = sample_rate
        
        # Use provided model path or default
        if model_path:
            self.model_path = model_path
        else:
            self.model_path = DEFAULT_MODEL_DIR
        
        # Ensure models directory exists
        MODELS_DIR.mkdir(exist_ok=True)
            
        # Check if model exists
        model_dir = Path(self.model_path)
        if not model_dir.exists() or not model_dir.is_dir():
            raise FileNotFoundError(f"Vosk model not found at {self.model_path}. "
                                    f"Please download a model from https://alphacephei.com/vosk/models "
                                    f"and extract it to the {MODELS_DIR} directory.")
        
        logger.info(f"Loading Vosk model from {self.model_path}")
        
        # Load the model and create recognizer
        self.model = Model(str(model_dir))
        self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
        self.recognizer.SetWords(True)  # Enable word timestamps
        
        logger.info("Vosk transcription service initialized")

    def reset(self):
        """Reset the recognizer to start a new transcription"""
        self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
        self.recognizer.SetWords(True)

    def accept_waveform(self, audio_chunk: bytes) -> dict:
        """
        Process an audio chunk and return any recognized text
        
        Args:
            audio_chunk: Raw audio bytes (mono, 16-bit PCM)
            
        Returns:
            dict: Recognition result with text and confidence
        """
        if self.recognizer.AcceptWaveform(audio_chunk):
            result_json = self.recognizer.Result()
            return json.loads(result_json)
        else:
            # Return partial result
            partial_json = self.recognizer.PartialResult()
            return json.loads(partial_json)
    
    def get_final_result(self) -> dict:
        """Get the final recognition result"""
        result_json = self.recognizer.FinalResult()
        return json.loads(result_json)

    async def transcribe_stream(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[dict, None]:
        """
        Transcribe an audio stream in real-time
        
        Args:
            audio_stream: Async generator yielding audio chunks
            
        Yields:
            dict: Recognition results as they become available
        """
        self.reset()  # Start fresh
        
        try:
            async for audio_chunk in audio_stream:
                result = self.accept_waveform(audio_chunk)
                
                # Only yield if we have actual text
                if result.get("text") or result.get("partial"):
                    yield result
                
                # Small delay to prevent overwhelming the CPU
                await asyncio.sleep(0.01)
                
            # Get final result after stream ends
            final_result = self.get_final_result()
            if final_result.get("text"):
                yield final_result
                
        except Exception as e:
            logger.error(f"Error in transcribe_stream: {str(e)}")
            raise

    def transcribe_file(self, audio_file_path: str) -> dict:
        """
        Transcribe an entire audio file
        
        Args:
            audio_file_path: Path to audio file (WAV format)
            
        Returns:
            dict: Complete transcription result
        """
        self.reset()
        
        try:
            with open(audio_file_path, "rb") as f:
                # Process file in chunks to avoid memory issues
                chunk_size = 4000  # bytes
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break
                    self.recognizer.AcceptWaveform(data)
                    
            return self.get_final_result()
            
        except Exception as e:
            logger.error(f"Error transcribing file {audio_file_path}: {str(e)}")
            raise


# Helper functions for audio processing

def convert_to_pcm(audio_data: np.ndarray) -> bytes:
    """
    Convert numpy audio data to PCM bytes for Vosk
    
    Args:
        audio_data: Audio data as numpy array (-1.0 to 1.0 float)
        
    Returns:
        bytes: Audio data as 16-bit PCM
    """
    # Scale to int16 range and convert to bytes
    audio_int16 = (audio_data * 32767).astype(np.int16)
    return audio_int16.tobytes()
