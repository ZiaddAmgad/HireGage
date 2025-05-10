// API service for communication with the backend
const API_URL = 'http://localhost:8000/api';

/**
 * Save a transcript to a JSON file on the server
 * @param sessionId The current interview session ID
 * @param transcript The transcript text
 * @param speaker The speaker ('user' or 'ai')
 */
export const saveTranscriptToFile = async (
  sessionId: string, 
  transcript: string, 
  speaker: 'user' | 'ai'
): Promise<Response> => {
  try {
    const response = await fetch(`${API_URL}/transcript/${sessionId}/save`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: transcript,
        speaker,
        timestamp: new Date().toISOString(),
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Error saving transcript: ${response.statusText}`);
    }
    
    return response;
  } catch (error) {
    console.error('Failed to save transcript:', error);
    throw error;
  }
};

/**
 * Get transcripts from the server
 * @param sessionId The current interview session ID
 */
export const getTranscripts = async (sessionId: string): Promise<any> => {
  try {
    const response = await fetch(`${API_URL}/transcript/${sessionId}`);
    
    if (!response.ok) {
      throw new Error(`Error fetching transcripts: ${response.statusText}`);
    }
    
    return response.json();
  } catch (error) {
    console.error('Failed to fetch transcripts:', error);
    throw error;
  }
};
