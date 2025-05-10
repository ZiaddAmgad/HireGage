import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, Mic, Video, BookOpen } from 'lucide-react';
import Button from '../components/common/Button';
import { useInterview } from '../context/InterviewContext';

const StartPage: React.FC = () => {
  const navigate = useNavigate();
  const { dispatch } = useInterview();
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  
  const handleStart = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!jobTitle.trim() && !jobDescription.trim()) {
      setError('Please provide either a job title or job description');
      return;
    }
    
    setError('');
    setIsSubmitting(true);
    
    try {
      // In a real implementation, you might do some pre-processing or API validation here
      
      // Update the context with job info
      dispatch({
        type: 'SET_JOB_INFO',
        payload: { jobTitle, jobDescription }
      });
      
      // Start the interview
      dispatch({ type: 'START_INTERVIEW' });
      
      // Navigate to the interview page
      navigate('/interview');
    } catch (err) {
      console.error('Error starting interview:', err);
      setError('Failed to start interview. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-12">
        <div className="inline-flex items-center justify-center p-4 bg-blue-100 rounded-full mb-4">
          <Briefcase className="h-10 w-10 text-blue-800" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-3">Practice Your Interview Skills</h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Enter a job title or description, and our AI will conduct a personalized interview to help you prepare.
        </p>
      </div>
      
      <div className="bg-white rounded-xl shadow-md p-8">
        <form onSubmit={handleStart}>
          <div className="mb-6">
            <label htmlFor="jobTitle" className="block text-sm font-medium text-gray-700 mb-1">
              Job Title
            </label>
            <input
              type="text"
              id="jobTitle"
              className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              placeholder="E.g., Software Engineer, Product Manager, Marketing Specialist"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
            />
          </div>
          
          <div className="mb-8">
            <label htmlFor="jobDescription" className="block text-sm font-medium text-gray-700 mb-1">
              Job Description (optional)
            </label>
            <textarea
              id="jobDescription"
              rows={5}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              placeholder="Paste job description for more tailored questions..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
            ></textarea>
            <p className="mt-2 text-sm text-gray-500">
              The more details you provide, the more relevant your practice interview will be.
            </p>
          </div>
          
          {error && (
            <div className="mb-6 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600">
              {error}
            </div>
          )}
          
          <Button 
            type="submit" 
            variant="primary" 
            fullWidth 
            size="lg"
            isLoading={isSubmitting}
          >
            Start Interview Practice
          </Button>
        </form>
        
        <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex flex-col items-center text-center p-4">
            <div className="bg-blue-100 p-3 rounded-full mb-3">
              <Mic className="h-6 w-6 text-blue-800" />
            </div>
            <h3 className="font-medium text-gray-900 mb-1">Voice Interaction</h3>
            <p className="text-sm text-gray-500">Speak naturally as you would in a real interview</p>
          </div>
          
          <div className="flex flex-col items-center text-center p-4">
            <div className="bg-teal-100 p-3 rounded-full mb-3">
              <Video className="h-6 w-6 text-teal-700" />
            </div>
            <h3 className="font-medium text-gray-900 mb-1">Video Practice</h3>
            <p className="text-sm text-gray-500">Practice your visual presence and body language</p>
          </div>
          
          <div className="flex flex-col items-center text-center p-4">
            <div className="bg-amber-100 p-3 rounded-full mb-3">
              <BookOpen className="h-6 w-6 text-amber-700" />
            </div>
            <h3 className="font-medium text-gray-900 mb-1">Get Feedback</h3>
            <p className="text-sm text-gray-500">Receive detailed assessment and improvement tips</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StartPage;