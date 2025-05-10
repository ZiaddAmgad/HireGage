import React, { useRef, useEffect } from 'react';
import { useInterview } from '../../context/InterviewContext';

const VideoPlayer: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const { state } = useInterview();
  
  useEffect(() => {
    let stream: MediaStream | null = null;
    
    const setupCamera = async () => {
      try {
        if (state.isCameraActive) {
          stream = await navigator.mediaDevices.getUserMedia({ 
            video: true,
            audio: true
          });
          
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
        } else if (videoRef.current && videoRef.current.srcObject) {
          videoRef.current.srcObject = null;
        }
      } catch (err) {
        console.error('Error accessing camera:', err);
      }
    };
    
    setupCamera();
    
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [state.isCameraActive]);
  
  return (
    <div className="relative w-full h-0 pb-[56.25%] bg-gray-900 rounded-lg overflow-hidden">
      {state.isCameraActive ? (
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="absolute top-0 left-0 w-full h-full object-cover"
        />
      ) : (
        <div className="absolute top-0 left-0 w-full h-full flex items-center justify-center bg-gray-900 text-white">
          <div className="text-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-16 w-16 mx-auto mb-4 text-gray-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M3 3l18 18"
              />
            </svg>
            <p>Camera is turned off</p>
          </div>
        </div>
      )}
      
      {/* Recording indicator */}
      {state.isInterviewStarted && state.isCameraActive && (
        <div className="absolute top-4 left-4 flex items-center space-x-2">
          <div className="h-3 w-3 bg-red-500 rounded-full animate-pulse"></div>
          <span className="text-white text-sm font-medium">REC</span>
        </div>
      )}
    </div>
  );
};

export default VideoPlayer;