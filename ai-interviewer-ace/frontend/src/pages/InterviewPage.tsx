// Completely rewritten InterviewPage.tsx
import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInterview } from '../context/InterviewContext';
import VideoPlayer from '../components/interview/VideoPlayer';
import TranscriptPane from '../components/interview/TranscriptPane';
import InterviewControls from '../components/interview/InterviewControls';
import useSpeechRecognition from '../hooks/useSpeechRecognition';
import * as interviewApi from '../services/interviewApi';

const InterviewPage: React.FC = () => {
  const navigate = useNavigate();
  const { state, dispatch } = useInterview();
  const [isIntroducing, setIsIntroducing] = useState(true);
  const [sessionId, setSessionId] = useState<string>('');
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const sourceBufferRef = useRef<SourceBuffer | null>(null);

  // Speech recognition setup
  const { startListening, stopListening, isListening, transcript } = useSpeechRecognition({
    onTranscriptUpdate: (transcriptText) => {
      // Show real-time typing effect in the UI
      dispatch({ 
        type: 'ADD_TO_TRANSCRIPT', 
        payload: { 
          speaker: 'user', 
          text: transcriptText 
        } 
      });
      
      // Send transcripts to backend via websocket
      if (websocket && websocket.readyState === WebSocket.OPEN && sessionId) {
        // Determine if this might be a final result based on punctuation
        const isFinalSentence = /[.!?]$/.test(transcriptText.trim());
        
        websocket.send(JSON.stringify({
          text: transcriptText,
          is_final: isFinalSentence
        }));
      }
    },
    sessionId: sessionId,
    saveInterimResults: true
  });

  // Connect to backend and start the interview
  useEffect(() => {
    // Check if we have job information
    if (!state.jobTitle && !state.jobDescription) {
      navigate('/');
      return;
    }
    
    // Setup audio handling for speech synthesis
    const setupAudio = () => {
      const mediaSource = new MediaSource();
      const audioEl = audioRef.current;
      if (!audioEl) return null;

      audioEl.src = URL.createObjectURL(mediaSource);

      return new Promise<MediaSource>((resolve) => {
        mediaSource.addEventListener("sourceopen", () => {
          const mime = "audio/webm; codecs=opus";
          try {
            const sourceBuffer = mediaSource.addSourceBuffer(mime);
            sourceBuffer.mode = "sequence";
            sourceBufferRef.current = sourceBuffer;
            resolve(mediaSource);
          } catch (e) {
            console.error('Error setting up source buffer:', e);
            resolve(mediaSource);
          }
        });
      });
    };
    
    // Initialize the interview with the backend
    const initInterview = async () => {
      try {
        // Indicate we're in introduction phase
        setIsIntroducing(true);
        dispatch({ type: 'START_INTERVIEW' });
        dispatch({ type: 'SET_AI_PROCESSING', payload: true });
        
        // Start the interview with our API
        const response = await interviewApi.startInterview({
          job_title: state.jobTitle,
          company_name: "HireGage", // Could be configurable
          job_description: state.jobDescription,
          interview_duration: 15 // Minutes
        });
        
        // Save session ID for future API calls
        setSessionId(response.session_id);
        
        // Create WebSocket connection for real-time communication
        const ws = interviewApi.createInterviewWebSocket(response.session_id);
        setWebsocket(ws);
        
        // Configure WebSocket for binary messages (audio)
        ws.binaryType = "arraybuffer";
        
        // Setup audio player for AI speech
        const mediaSource = await setupAudio();
        
        // Handle incoming messages from WebSocket
        ws.onmessage = (event) => {
          // Handle binary audio data
          if (event.data instanceof ArrayBuffer && sourceBufferRef.current && !sourceBufferRef.current.updating) {
            try {
              // Append audio data to the buffer for playback
              sourceBufferRef.current.appendBuffer(new Uint8Array(event.data));
            } catch (e) {
              console.error('Error appending buffer:', e);
            }
          } 
          // Handle text messages (questions, instructions)
          else if (typeof event.data === 'string') {
            try {
              const data = JSON.parse(event.data);
              if (data.text) {
                // Add AI message to the transcript
                dispatch({ 
                  type: 'ADD_TO_TRANSCRIPT', 
                  payload: { 
                    speaker: 'ai', 
                    text: data.text 
                  } 
                });
                
                // Set as the current active question
                dispatch({ type: 'SET_CURRENT_QUESTION', payload: data.text });
              }
            } catch (e) {
              console.error('Error processing WebSocket message:', e);
            }
          }
        };
        
        // Handle WebSocket close
        ws.onclose = () => {
          console.log("WebSocket connection closed");
          if (mediaSource && mediaSource.readyState === 'open') {
            mediaSource.endOfStream();
          }
        };
        
        // Display the initial AI introduction message
        dispatch({ 
          type: 'ADD_TO_TRANSCRIPT', 
          payload: { 
            speaker: 'ai', 
            text: response.message 
          } 
        });
        
        dispatch({ type: 'SET_CURRENT_QUESTION', payload: response.message });
        dispatch({ type: 'SET_AI_PROCESSING', payload: false });
        
        // End introduction phase
        setIsIntroducing(false);
        
        // Start listening for user's speech
        startListening();
      } catch (error) {
        console.error('Error initializing interview:', error);
        dispatch({ type: 'SET_AI_PROCESSING', payload: false });
        
        // Display error to user
        alert('Failed to start interview. Please try again later.');
      }
    };
    
    // Start the interview automatically
    initInterview();
    
    // Cleanup when component unmounts
    return () => {
      if (websocket) {
        websocket.close();
      }
      stopListening();
    };
  }, [state.jobTitle, state.jobDescription, navigate, dispatch, startListening, stopListening]);
  
  // Function to handle ending the interview
  const handleEndInterview = async () => {
    stopListening();
    
    if (sessionId) {
      try {
        dispatch({ type: 'SET_AI_PROCESSING', payload: true });
        
        // Call the API to get interview feedback and summary
        const summary = await interviewApi.endInterview(sessionId);
        
        // Update the interview context with feedback
        const feedback = {
          overall: summary.feedback,
          strengths: summary.evaluation ? [
            `Technical skills: ${summary.evaluation.technical_skills}/10`,
            `Communication: ${summary.evaluation.communication}/10`,
            `Culture fit: ${summary.evaluation.culture_fit}/10`,
            `Problem solving: ${summary.evaluation.problem_solving}/10`,
          ] : [],
          improvements: summary.summary ? summary.summary.key_points : [],
          questionFeedback: summary.transcript ? 
            summary.transcript
              .filter(item => item.role === 'assistant')
              .map(item => ({
                question: item.content,
                feedback: 'AI analysis of your response to be implemented'
              })) : []
        };
        
        dispatch({ type: 'SET_FEEDBACK', payload: feedback });
        dispatch({ type: 'END_INTERVIEW' });
        dispatch({ type: 'SET_AI_PROCESSING', payload: false });
        
        // Navigate to feedback page
        navigate('/feedback');
      } catch (error) {
        console.error('Error ending interview:', error);
        dispatch({ type: 'SET_AI_PROCESSING', payload: false });
        
        // End the interview anyway and navigate to feedback with mock data
        const mockFeedback = {
          overall: "Thank you for completing the interview. We're experiencing technical difficulties retrieving your detailed feedback.",
          strengths: [
            "Interview completed successfully",
          ],
          improvements: [
            "Try again later for detailed feedback"
          ],
          questionFeedback: []
        };
        
        dispatch({ type: 'SET_FEEDBACK', payload: mockFeedback });
        dispatch({ type: 'END_INTERVIEW' });
        navigate('/feedback');
      }
    } else {
      // No session ID, just navigate to feedback with error message
      const errorFeedback = {
        overall: "Interview session could not be properly established. Please try again.",
        strengths: [],
        improvements: ["Check your internet connection and try again"],
        questionFeedback: []
      };
      
      dispatch({ type: 'SET_FEEDBACK', payload: errorFeedback });
      dispatch({ type: 'END_INTERVIEW' });
      navigate('/feedback');
    }
  };
  
  // Handle when user requests next question
  const handleNextQuestion = async () => {
    if (sessionId) {
      try {
        dispatch({ type: 'SET_AI_PROCESSING', payload: true });
        
        // Submit final transcript and get next question
        const response = await interviewApi.getNextQuestion(sessionId);
        
        if (response.message) {
          dispatch({ 
            type: 'ADD_TO_TRANSCRIPT', 
            payload: { 
              speaker: 'ai', 
              text: response.message
            } 
          });
          
          dispatch({ type: 'SET_CURRENT_QUESTION', payload: response.message });
        }
        
        dispatch({ type: 'SET_AI_PROCESSING', payload: false });
      } catch (error) {
        console.error('Error getting next question:', error);
        dispatch({ type: 'SET_AI_PROCESSING', payload: false });
      }
    }
  };
  
  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      {/* Interview header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">
          {state.jobTitle || 'Job Interview'} Interview
        </h1>
        <p className="text-gray-600 mt-1">
          Speak naturally as if in a real interview. The AI will guide the conversation.
        </p>
      </div>
      
      {/* Loading indicator during introduction */}
      {isIntroducing && (
        <div className="mb-6 bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-700">
                The AI interviewer is preparing your interview based on the job description. This will take just a moment...
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* Processing indicator */}
      {state.isAIProcessing && !isIntroducing && (
        <div className="mb-6 bg-gray-50 border-l-4 border-gray-500 p-4 rounded">
          <div className="flex items-center">
            <div className="flex-shrink-0 mr-3">
              <svg className="animate-spin h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <p className="text-sm text-gray-700">
              Processing your response...
            </p>
          </div>
        </div>
      )}
      
      {/* Main interview area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Video preview */}
        <div className="lg:col-span-1">
          <div className="bg-gray-100 rounded-lg overflow-hidden">
            <VideoPlayer />
          </div>
          
          {/* Microphone status indicator */}
          <div className={`mt-3 flex items-center p-3 rounded ${isListening ? 'bg-green-50 text-green-700' : 'bg-gray-50 text-gray-500'}`}>
            <div className={`w-3 h-3 rounded-full mr-2 ${isListening ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
            <span className="text-sm">{isListening ? 'Microphone active - speak now' : 'Microphone inactive'}</span>
          </div>
        </div>
        
        {/* Transcript and controls */}
        <div className="lg:col-span-2 flex flex-col">
          {/* Current question highlight */}
          {state.currentQuestion && (
            <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 mb-4">
              <h3 className="font-medium text-blue-800 mb-1">Current Question:</h3>
              <p className="text-gray-800">{state.currentQuestion}</p>
            </div>
          )}
          
          {/* Real-time transcript */}
          <div className="flex-grow mb-4">
            <TranscriptPane />
          </div>
          
          {/* Controls */}
          <div className="mt-auto">
            <div className="flex justify-between items-center">
              <button 
                onClick={handleNextQuestion}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={state.isAIProcessing}
              >
                Next Question
              </button>
              
              <button 
                onClick={handleEndInterview}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                End Interview
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Hidden audio element for AI speech */}
      <audio ref={audioRef} style={{ display: 'none' }} autoPlay />
    </div>
  );
};

export default InterviewPage;