// API service for interview-related functionality
import { JobTitleRequest, InterviewResponse, InterviewSummary } from '../types/api.js';

const API_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000';

/**
 * Start a new interview session
 * @param data Interview job data
 * @returns Interview session response with session ID
 */
export const startInterview = async (data: JobTitleRequest): Promise<InterviewResponse> => {
  try {
    // Set a timeout for the fetch request
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

    const response = await fetch(`${API_URL}/interview/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId); // Clear the timeout if the request succeeds
    
    if (!response.ok) {
      throw new Error(`Error starting interview: ${response.statusText}`);
    }
    
    return response.json();
  } catch (error: any) {
    if (error.name === 'AbortError' || error instanceof TypeError) {
      console.error('Server connection failed. Please ensure the backend server is running.');
      throw new Error('Cannot connect to the interview server. Please ensure the backend is running at ' + API_URL);
    } else {
      console.error('Failed to start interview:', error);
      throw error;
    }
  }
};

/**
 * Create a websocket connection for real-time interview
 * @param sessionId The current interview session ID
 * @returns WebSocket connection
 */
export const createInterviewWebSocket = (sessionId: string): WebSocket => {
  const ws = new WebSocket(`${WS_URL}/interview/ws/${sessionId}`);
  
  ws.onopen = () => {
    console.log('WebSocket connection established');
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  return ws;
};

/**
 * Submit the final answer from the user
 * @param sessionId The current interview session ID
 * @param text The final response text
 * @returns Promise with the agent's next response
 */
export const submitAnswer = async (sessionId: string, text: string): Promise<{ message: string }> => {
  try {
    const response = await fetch(`${API_URL}/interview/${sessionId}/respond`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text, is_final: true }),
    });
    
    if (!response.ok) {
      throw new Error(`Error submitting answer: ${response.statusText}`);
    }
    
    return response.json();
  } catch (error) {
    console.error('Failed to submit answer:', error);
    throw error;
  }
};

/**
 * Request next interview question
 * @param sessionId The current interview session ID
 * @returns Promise with the agent's next question
 */
export const getNextQuestion = async (sessionId: string): Promise<{ message: string }> => {
  try {
    // Since the backend doesn't have a specific next-question endpoint,
    // we're submitting an empty response to get the next question
    const response = await fetch(`${API_URL}/interview/${sessionId}/respond`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: "I'm ready for the next question", is_final: true }),
    });
    
    if (!response.ok) {
      throw new Error(`Error getting next question: ${response.statusText}`);
    }
    
    return response.json();
  } catch (error) {
    console.error('Failed to get next question:', error);
    throw error;
  }
};

/**
 * End the interview and get summary
 * @param sessionId The current interview session ID
 * @returns Promise with interview summary
 */
export const endInterview = async (sessionId: string): Promise<InterviewSummary> => {
  try {
    const response = await fetch(`${API_URL}/interview/${sessionId}/end`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`Error ending interview: ${response.statusText}`);
    }
    
    return response.json();
  } catch (error) {
    console.error('Failed to end interview:', error);
    throw error;
  }
};
