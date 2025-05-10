import { useState, useEffect, useRef, useCallback } from 'react';
import { useInterview } from '../context/InterviewContext';
import * as api from '../services/api';
// TypeScript declaration files are automatically included, no need to import them

interface UseSpeechRecognitionProps {
  onTranscriptUpdate?: (transcript: string) => void;
  sessionId?: string;
  saveInterimResults?: boolean; // New option to save interim results
}

export const useSpeechRecognition = ({ 
  onTranscriptUpdate, 
  sessionId, 
  saveInterimResults = false 
}: UseSpeechRecognitionProps = {}) => {
  const { state, dispatch } = useInterview();
  const [transcript, setTranscript] = useState('');
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const lastSavedTranscriptRef = useRef<string>('');
  
  // Helper function to save transcript to backend
  const saveTranscript = useCallback(async (text: string, finalResult: boolean = true) => {
    if (!sessionId || !text.trim()) return;
    
    // Don't save the same transcript multiple times
    if (text.trim() === lastSavedTranscriptRef.current.trim()) return;
    
    // Only save interim results if explicitly enabled
    if (!finalResult && !saveInterimResults) return;
    
    try {
      await api.saveTranscriptToFile(sessionId, text, 'user');
      console.log(`Transcript ${finalResult ? 'final' : 'interim'} saved to file`);
      lastSavedTranscriptRef.current = text;
      
      // Add to transcript in context state if it's a final result
      if (finalResult) {
        dispatch({
          type: 'ADD_TO_TRANSCRIPT',
          payload: { speaker: 'user', text }
        });
      }
    } catch (error) {
      console.error('Failed to save transcript to file:', error);
    }
  }, [sessionId, dispatch, saveInterimResults]);
  const startListening = useCallback(() => {
    if (!state.isMicActive) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      console.error('Speech recognition not supported in this browser');
      return;
    }

    try {
      recognitionRef.current = new SpeechRecognition();
      const recognition = recognitionRef.current;
      
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListening(true);
        setTranscript('');
        lastSavedTranscriptRef.current = '';
      };

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        const currentTranscript = finalTranscript || interimTranscript;
        setTranscript(currentTranscript);
        
        // // If we have a final transcript, save it immediately
        // if (finalTranscript && finalTranscript.trim()) {
        //   saveTranscript(finalTranscript, true);
        // } 
        // // If we have interim results and saving them is enabled
        // else if (saveInterimResults && interimTranscript && interimTranscript.trim()) {
        //   saveTranscript(interimTranscript, false);
        // }
        
        if (onTranscriptUpdate) {
          onTranscriptUpdate(currentTranscript);
        }
      };

      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        console.error('Speech recognition error', event.error);
        setIsListening(false);
      };

      recognition.onend = async () => {
        // Final save of transcript if needed
        if (transcript.trim() && transcript.trim() !== lastSavedTranscriptRef.current.trim()) {
          await saveTranscript(transcript, true);
        }
        setIsListening(false);
      };

      recognition.start();
    } catch (error) {
      console.error('Error starting speech recognition:', error);
    }
  }, [dispatch, onTranscriptUpdate, saveTranscript, state.isMicActive]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
  }, []);

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  return {
    transcript,
    isListening,
    startListening,
    stopListening
  };
};

export default useSpeechRecognition;