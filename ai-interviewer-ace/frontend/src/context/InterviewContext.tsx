import React, { createContext, useContext, useReducer } from 'react';

// Types
export interface InterviewState {
  jobTitle: string;
  jobDescription: string;
  isInterviewStarted: boolean;
  isInterviewEnded: boolean;
  currentQuestion: string;
  transcript: Array<{ speaker: 'ai' | 'user', text: string }>;
  isMicActive: boolean;
  isCameraActive: boolean;
  isAIProcessing: boolean;
  feedback: {
    overall: string;
    strengths: string[];
    improvements: string[];
    questionFeedback: Array<{ question: string, feedback: string }>;
  } | null;
}

type InterviewAction =
  | { type: 'SET_JOB_INFO', payload: { jobTitle: string, jobDescription: string } }
  | { type: 'START_INTERVIEW' }
  | { type: 'END_INTERVIEW' }
  | { type: 'SET_CURRENT_QUESTION', payload: string }
  | { type: 'ADD_TO_TRANSCRIPT', payload: { speaker: 'ai' | 'user', text: string } }
  | { type: 'TOGGLE_MIC' }
  | { type: 'TOGGLE_CAMERA' }
  | { type: 'SET_AI_PROCESSING', payload: boolean }
  | { type: 'SET_FEEDBACK', payload: InterviewState['feedback'] }
  | { type: 'RESET_INTERVIEW' };

const initialState: InterviewState = {
  jobTitle: '',
  jobDescription: '',
  isInterviewStarted: false,
  isInterviewEnded: false,
  currentQuestion: '',
  transcript: [],
  isMicActive: true,
  isCameraActive: true,
  isAIProcessing: false,
  feedback: null
};

const interviewReducer = (state: InterviewState, action: InterviewAction): InterviewState => {
  switch (action.type) {
    case 'SET_JOB_INFO':
      return {
        ...state,
        jobTitle: action.payload.jobTitle,
        jobDescription: action.payload.jobDescription
      };
    case 'START_INTERVIEW':
      return {
        ...state,
        isInterviewStarted: true,
        isInterviewEnded: false
      };
    case 'END_INTERVIEW':
      return {
        ...state,
        isInterviewStarted: false,
        isInterviewEnded: true
      };
    case 'SET_CURRENT_QUESTION':
      return {
        ...state,
        currentQuestion: action.payload
      };
    case 'ADD_TO_TRANSCRIPT':
      return {
        ...state,
        transcript: [...state.transcript, action.payload]
      };
    case 'TOGGLE_MIC':
      return {
        ...state,
        isMicActive: !state.isMicActive
      };
    case 'TOGGLE_CAMERA':
      return {
        ...state,
        isCameraActive: !state.isCameraActive
      };
    case 'SET_AI_PROCESSING':
      return {
        ...state,
        isAIProcessing: action.payload
      };
    case 'SET_FEEDBACK':
      return {
        ...state,
        feedback: action.payload
      };
    case 'RESET_INTERVIEW':
      return {
        ...initialState
      };
    default:
      return state;
  }
};

interface InterviewContextProps {
  state: InterviewState;
  dispatch: React.Dispatch<InterviewAction>;
}

const InterviewContext = createContext<InterviewContextProps | undefined>(undefined);

export const InterviewProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(interviewReducer, initialState);

  return (
    <InterviewContext.Provider value={{ state, dispatch }}>
      {children}
    </InterviewContext.Provider>
  );
};

export const useInterview = () => {
  const context = useContext(InterviewContext);
  if (context === undefined) {
    throw new Error('useInterview must be used within an InterviewProvider');
  }
  return context;
};