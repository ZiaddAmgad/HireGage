import React, { useRef, useEffect } from 'react';
import { useInterview } from '../../context/InterviewContext';

const TranscriptPane: React.FC = () => {
  const { state } = useInterview();
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to the bottom when transcript updates
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [state.transcript]);
  
  return (
    <div className="bg-white rounded-lg shadow-md p-4 h-96 overflow-hidden flex flex-col">
      <h2 className="text-lg font-semibold text-gray-800 pb-2 border-b">Conversation Transcript</h2>
      
      <div 
        ref={containerRef}
        className="flex-1 overflow-y-auto p-2 space-y-4 mt-2"
      >
        {state.transcript.length > 0 ? (
          state.transcript.map((entry, index) => (
            <div 
              key={index} 
              className={`${
                entry.speaker === 'ai' 
                  ? 'bg-blue-50 border-l-4 border-blue-500' 
                  : 'bg-gray-50 border-l-4 border-gray-300'
              } p-3 rounded`}
            >
              <div className="font-medium text-sm mb-1 text-gray-500">
                {entry.speaker === 'ai' ? 'AI Interviewer' : 'You'}
              </div>
              <div className="text-gray-800">{entry.text}</div>
            </div>
          ))
        ) : (
          <div className="h-full flex items-center justify-center text-gray-400 italic">
            The conversation transcript will appear here...
          </div>
        )}
        
        {/* Current question indicator */}
        {state.currentQuestion && (
          <div className="bg-blue-50 border-l-4 border-blue-500 p-3 rounded animate-pulse">
            <div className="font-medium text-sm mb-1 text-gray-500">
              AI Interviewer
            </div>
            <div className="text-gray-800">{state.currentQuestion}</div>
          </div>
        )}
        
        {/* AI Processing indicator */}
        {state.isAIProcessing && (
          <div className="flex items-center space-x-2 p-3 text-blue-600">
            <div className="flex space-x-1">
              <div className="w-2 h-2 rounded-full bg-blue-600 animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 rounded-full bg-blue-600 animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 rounded-full bg-blue-600 animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
            <span className="text-sm">AI is thinking...</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default TranscriptPane;