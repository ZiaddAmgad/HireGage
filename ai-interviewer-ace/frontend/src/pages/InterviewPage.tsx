import React, { useEffect, useState,useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInterview } from '../context/InterviewContext';
import VideoPlayer from '../components/interview/VideoPlayer';
import TranscriptPane from '../components/interview/TranscriptPane';
import InterviewControls from '../components/interview/InterviewControls';
import useSpeechRecognition from '../hooks/useSpeechRecognition';





const InterviewPage: React.FC = () => {
  const navigate = useNavigate();
  const { state, dispatch } = useInterview();
  const [isIntroducing, setIsIntroducing] = useState(true);
  const audioRef = useRef<HTMLAudioElement>(null);
  const sourceBufferRef = useRef<SourceBuffer | null>(null);

  const { startListening, stopListening, isListening } = useSpeechRecognition({
    onTranscriptUpdate: (transcript) => {
      // This could be used to show real-time typing effect
      console.log('Current transcript:', transcript);

      const ws = new WebSocket("ws://localhost:8000/interview/ws/1");



    }
  });
  
  // Simulate an interview flow with the AI
  useEffect(() => {



    const mediaSource = new MediaSource();
    const audioEl = audioRef.current;
    if (!audioEl) return;

    audioEl.src = URL.createObjectURL(mediaSource);

    const ws = new WebSocket("ws://localhost:8000/interview/ws/1");
    mediaSource.addEventListener("sourceopen", () => {
      const mime = "audio/webm; codecs=opus";
      const sourceBuffer = mediaSource.addSourceBuffer(mime);
      sourceBuffer.mode = "sequence";
      sourceBufferRef.current = sourceBuffer;
      
      ws.binaryType = "arraybuffer";

      ws.onmessage = (event) => {
        if (event.data instanceof ArrayBuffer && !sourceBuffer.updating) {
          sourceBuffer.appendBuffer(new Uint8Array(event.data));
        }
      };

      ws.onclose = () => {
        mediaSource.endOfStream();
      };
    });
    // Check if we have job information
    if (!state.jobTitle && !state.jobDescription) {
      navigate('/');
      return;
    }
    
    const startInterview = async () => {
      try {
        // Introduction phase
        setIsIntroducing(true);
        
        // Simulate AI processing
        dispatch({ type: 'SET_AI_PROCESSING', payload: true });
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // AI introduction
        const introduction = `Hello! I'll be your interviewer today for the ${state.jobTitle || 'position'} role. I'll ask you some questions based on the job description you provided. Let's get started with a brief introduction about yourself.`;
        
        dispatch({ 
          type: 'ADD_TO_TRANSCRIPT', 
          payload: { 
            speaker: 'ai', 
            text: introduction 
          } 
        });
        
        dispatch({ type: 'SET_CURRENT_QUESTION', payload: 'Could you please introduce yourself and tell me a bit about your background relevant to this role?' });
        dispatch({ type: 'SET_AI_PROCESSING', payload: false });
        
        // End introduction phase
        setIsIntroducing(false);
        
        // Start listening for user's response
        startListening();
        
        // Simulate interview questions
        const questions = [
          'What interests you about this position?',
          'Tell me about a challenging project you worked on recently.',
          'How do you handle tight deadlines and pressure?',
          'Where do you see yourself professionally in the next 3-5 years?'
        ];
        
        // For demo purposes, we'll simulate an interview flow with timed questions
        for (let i = 0; i < questions.length; i++) {
          // Wait for "user response time" (simulated)
          await new Promise(resolve => setTimeout(resolve, 10000 + Math.random() * 5000));
          
          // Stop listening for current answer
          stopListening();
          
          // AI is processing
          dispatch({ type: 'SET_AI_PROCESSING', payload: true });
          await new Promise(resolve => setTimeout(resolve, 2000));
          
          // AI asks next question
          dispatch({ 
            type: 'ADD_TO_TRANSCRIPT', 
            payload: { 
              speaker: 'ai', 
              text: questions[i] 
            } 
          });
          
          dispatch({ type: 'SET_CURRENT_QUESTION', payload: questions[i] });
          dispatch({ type: 'SET_AI_PROCESSING', payload: false });
          
          // Start listening for next response
          startListening();
        }
        
        // Final waiting period for the last answer
        await new Promise(resolve => setTimeout(resolve, 10000));
        
        // Stop listening for the last answer
        stopListening();
        
        // AI is processing
        dispatch({ type: 'SET_AI_PROCESSING', payload: true });
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // AI concludes the interview
        dispatch({ 
          type: 'ADD_TO_TRANSCRIPT', 
          payload: { 
            speaker: 'ai', 
            text: 'Thank you for participating in this interview! I have all the information I need. Let me prepare your feedback...' 
          } 
        });
        
        dispatch({ type: 'SET_CURRENT_QUESTION', payload: '' });
        dispatch({ type: 'SET_AI_PROCESSING', payload: false });
        
        // Simulate generating feedback
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // End the interview and redirect to feedback
        handleEndInterview();
      } catch (error) {
        console.error('Error during interview:', error);
      }
    };
    
    // Start the interview simulation
    startInterview();
    
    // Cleanup when component unmounts
    return () => {
      stopListening();
    };
  }, []);
  
  const handleEndInterview = () => {
    stopListening();
    
    // Generate mock feedback
    const feedback = {
      overall: "Overall, you performed well in the interview with clear communication and relevant experience. There's room for improvement in specificity and structure of some answers.",
      strengths: [
        "Strong articulation of technical skills and experience",
        "Good examples of past projects and accomplishments",
        "Professional demeanor throughout the interview",
        "Clear interest in the position and company"
      ],
      improvements: [
        "Provide more measurable outcomes and metrics in your examples",
        "Structure answers using the STAR method for clarity",
        "Elaborate more on how your skills directly apply to the job requirements",
        "Prepare more concise answers to common questions"
      ],
      questionFeedback: [
        {
          question: "Could you please introduce yourself and tell me a bit about your background relevant to this role?",
          feedback: "Good overview of relevant experience, but could be more concise. Consider focusing on 2-3 key highlights most relevant to this role."
        },
        {
          question: "What interests you about this position?",
          feedback: "Strong answer showing research about the company. Good job connecting your skills to the role requirements."
        },
        {
          question: "Tell me about a challenging project you worked on recently.",
          feedback: "Good example, but lacking specific metrics on impact. Include numbers and business outcomes to strengthen your response."
        }
      ]
    };
    
    dispatch({ type: 'SET_FEEDBACK', payload: feedback });
    dispatch({ type: 'END_INTERVIEW' });
    
    // Navigate to feedback page
    navigate('/feedback');
  };
  
  return (
    <div className="max-w-5xl mx-auto">
      {/* Job information */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Interview Practice: {state.jobTitle || 'Job Position'}
        </h1>
        <p className="text-gray-600 mt-1">
          Speak naturally as if in a real interview. The AI will guide the conversation.
        </p>
      </div>
      
      {/* Interview status banner */}
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
                The AI interviewer is preparing your questions based on the job information you provided. The interview will begin momentarily.
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* Main interview area */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Video section */}
        <div className="space-y-4">
          <VideoPlayer />
          
          {/* Microphone status */}
          <div className={`flex items-center p-3 rounded ${isListening ? 'bg-green-50 text-green-700' : 'bg-gray-50 text-gray-500'}`}>
            <div className={`w-3 h-3 rounded-full mr-2 ${isListening ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
            <span>{isListening ? 'Microphone active - speak now' : 'Microphone inactive'}</span>
          </div>
        </div>
        
        {/* Transcript section */}
        <div className="space-y-4">
          <TranscriptPane />
          
          {/* Current question focus area */}
          {state.currentQuestion && (
            <div className="bg-blue-50 border border-blue-100 rounded-lg p-4">
              <h3 className="font-medium text-blue-800 mb-1">Current Question:</h3>
              <p className="text-gray-800">{state.currentQuestion}</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Controls */}
      <div className="mt-6">
        <InterviewControls onEndInterview={handleEndInterview} />
      </div>
      <audio ref={audioRef} controls autoPlay />    </div>
  );
};

export default InterviewPage;