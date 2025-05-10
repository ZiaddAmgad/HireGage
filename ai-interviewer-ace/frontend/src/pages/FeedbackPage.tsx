import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, XCircle, Lightbulb, ArrowRight } from 'lucide-react';
import { useInterview } from '../context/InterviewContext';
import Button from '../components/common/Button';

const FeedbackPage: React.FC = () => {
  const navigate = useNavigate();
  const { state, dispatch } = useInterview();
  
  useEffect(() => {
    // If there's no feedback, redirect to start page
    if (!state.feedback) {
      navigate('/');
    }
  }, [state.feedback, navigate]);
  
  const handleStartNew = () => {
    // Reset the interview state
    dispatch({ type: 'RESET_INTERVIEW' });
    
    // Navigate to start page
    navigate('/');
  };
  
  if (!state.feedback) {
    return null;
  }
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-10">
        <div className="inline-flex items-center justify-center p-3 bg-green-100 rounded-full mb-4">
          <CheckCircle className="h-8 w-8 text-green-600" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-3">
          Your Interview Feedback
        </h1>
        <p className="text-lg text-gray-600">
          Here's an assessment of your performance for the {state.jobTitle || 'job'} interview.
        </p>
      </div>
      
      {/* Overall assessment */}
      <div className="bg-white rounded-xl shadow-md p-6 mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Overall Assessment</h2>
        <p className="text-gray-700 leading-relaxed">{state.feedback.overall}</p>
      </div>
      
      {/* Strengths and improvements */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        {/* Strengths */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="flex items-center mb-4">
            <div className="bg-green-100 p-2 rounded-full mr-3">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900">Strengths</h2>
          </div>
          
          <ul className="space-y-3">
            {state.feedback.strengths.map((strength, index) => (
              <li key={index} className="flex">
                <span className="text-green-500 mr-2">•</span>
                <span className="text-gray-700">{strength}</span>
              </li>
            ))}
          </ul>
        </div>
        
        {/* Areas for improvement */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="flex items-center mb-4">
            <div className="bg-amber-100 p-2 rounded-full mr-3">
              <Lightbulb className="h-6 w-6 text-amber-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900">Areas for Improvement</h2>
          </div>
          
          <ul className="space-y-3">
            {state.feedback.improvements.map((improvement, index) => (
              <li key={index} className="flex">
                <span className="text-amber-500 mr-2">•</span>
                <span className="text-gray-700">{improvement}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
      
      {/* Question-specific feedback */}
      <div className="bg-white rounded-xl shadow-md p-6 mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Question-by-Question Feedback</h2>
        
        <div className="space-y-6">
          {state.feedback.questionFeedback.map((item, index) => (
            <div key={index} className="border-b border-gray-100 pb-5 last:border-b-0 last:pb-0">
              <h3 className="font-medium text-gray-900 mb-2">
                {item.question}
              </h3>
              <p className="text-gray-700">{item.feedback}</p>
            </div>
          ))}
        </div>
      </div>
      
      {/* Action buttons */}
      <div className="flex justify-center">
        <Button 
          variant="primary" 
          size="lg"
          icon={ArrowRight}
          iconPosition="right"
          onClick={handleStartNew}
        >
          Practice Another Interview
        </Button>
      </div>
    </div>
  );
};

export default FeedbackPage;