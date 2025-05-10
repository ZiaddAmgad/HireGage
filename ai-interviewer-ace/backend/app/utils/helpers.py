"""
Utility functions for the HireGage application
"""
import json
from typing import Dict, List, Any, Optional
import logging


# Set up logging
logger = logging.getLogger("hiregage")


def format_interview_prompt(job_title: str, company_name: str, job_description: Optional[str] = None) -> str:
    """
    Format interview prompt for the AI agent
    
    Args:
        job_title: The job title for the interview
        company_name: The company name for the interview
        job_description: Optional job description
    
    Returns:
        str: Formatted prompt for the AI agent
    """
    job_desc_text = f"\n\nJob Description: {job_description}" if job_description else ""
    
    prompt = f"""
    You are an AI-powered HR interviewer conducting a job interview for a {job_title} position at {company_name}.
    {job_desc_text}
    
    Conduct a professional interview to assess the candidate's suitability for this role.
    Focus on relevant skills, experience, and fit for the position.
    """
    
    return prompt


def sanitize_openai_response(text: str) -> str:
    """
    Sanitize response from OpenAI by removing any unwanted formatting
    
    Args:
        text: Raw text from OpenAI
    
    Returns:
        str: Cleaned text
    """
    # Remove any markdown formatting that might be present
    text = text.strip()
    
    # Remove any JSON formatting if the response accidentally included it
    if text.startswith('```json'):
        text = text.replace('```json', '', 1)
        if text.endswith('```'):
            text = text[:-3]
    
    return text.strip()


def parse_json_safely(text: str) -> Dict[str, Any]:
    """
    Safely parse JSON from a string, with fallbacks for malformed JSON
    
    Args:
        text: JSON string
    
    Returns:
        dict: Parsed JSON object or empty dict if parsing fails
    """
    try:
        # First try to parse the entire string as JSON
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning("Failed to parse JSON directly, attempting extraction")
        
        # Try to find JSON within the text (between curly braces)
        try:
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx >= 0 and end_idx > start_idx:
                json_text = text[start_idx:end_idx+1]
                return json.loads(json_text)
        except Exception:
            logger.error("Failed to extract JSON from text")
            
        # Return empty dict as fallback
        return {}
