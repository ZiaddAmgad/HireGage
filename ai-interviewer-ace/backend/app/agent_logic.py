import asyncio
import json
import os
from typing import Dict, List, Tuple, Optional, Any
import openai
from openai import AsyncOpenAI
from app.config import get_settings

# Initialize OpenAI client
client = AsyncOpenAI(api_key=get_settings().OPENAI_API_KEY)

class InterviewAgent:
    """AI-powered interview agent that conducts job interviews."""
    
    def __init__(
        self, 
        job_title: str, 
        company_name: Optional[str] = None,
        job_description: Optional[str] = None,
        interview_duration: int = 15
    ):
        self.job_title = job_title
        self.company_name = company_name or "a company"
        self.job_description = job_description
        self.interview_duration = interview_duration
        self.conversation_history = []
        self.question_count = 0
        self.max_questions = self._determine_max_questions(interview_duration)
        
    def _determine_max_questions(self, duration_minutes: int) -> int:
        """Calculate the appropriate number of questions based on interview duration."""
        # Roughly estimate 2-3 minutes per question exchange
        return max(3, min(10, duration_minutes // 3))
    
    async def initialize_interview(self) -> str:
        """Generate the initial greeting and first question for the interview."""
        system_prompt = self._get_system_prompt()
        user_prompt = f"Start the interview for a {self.job_title} position at {self.company_name}. Introduce yourself briefly as an AI interviewer and ask your first question."
        
        try:
            response = await client.chat.completions.create(
                model=get_settings().OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            
            initial_message = response.choices[0].message.content.strip()
            
            # Add to conversation history
            self.conversation_history.extend([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": initial_message}
            ])
            
            self.question_count += 1
            return initial_message
            
        except Exception as e:
            print(f"Error during interview initialization: {str(e)}")
            return "Hello, I'll be your interviewer today. Let's start by discussing your experience. Could you tell me about your background related to this position?"
    
    async def process_candidate_response(self, response_text: str) -> str:
        """Process the candidate's response and generate the next question or follow-up."""
        self.conversation_history.append({"role": "user", "content": response_text})
        
        # Determine if we should ask another question or conclude the interview
        if self.question_count >= self.max_questions:
            next_prompt = "This is the final question. Wrap up the interview with a concluding question, then thank the candidate."
        else:
            next_prompt = "Based on the candidate's response, ask a relevant follow-up question."
        
        try:
            messages = self.conversation_history + [{"role": "user", "content": next_prompt}]
            
            response = await client.chat.completions.create(
                model=get_settings().OPENAI_MODEL,
                messages=messages,
                temperature=0.7
            )
            
            agent_response = response.choices[0].message.content.strip()
            
            # Add to conversation history
            self.conversation_history.append({"role": "assistant", "content": agent_response})
            
            self.question_count += 1
            return agent_response
            
        except Exception as e:
            print(f"Error processing candidate response: {str(e)}")
            return "Thank you for that response. Let's move on to the next question about your experience with this type of role."
    
    async def generate_interview_summary(self) -> Tuple[Dict[str, Any], Dict[str, Any], str]:
        """Generate a summary and evaluation of the interview."""
        try:
            # Extract just the conversation content
            conversation_text = "\n\n".join([
                f"{msg['role'].upper()}: {msg['content']}" 
                for msg in self.conversation_history 
                if msg['role'] in ['user', 'assistant']
            ])
            
            summary_prompt = f"""
            Based on the following interview for a {self.job_title} position, please provide:
            
            1. A JSON summary with key points discussed
            2. A JSON evaluation with scores (1-10) on:
               - Technical skills
               - Communication
               - Culture fit
               - Problem-solving
               - Overall impression
            3. A brief paragraph of constructive feedback for the candidate
            
            Format your response as valid JSON with three keys: "summary", "evaluation", and "feedback".
            
            INTERVIEW TRANSCRIPT:
            {conversation_text}
            """
            
            response = await client.chat.completions.create(
                model=get_settings().OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert HR analyzer providing detailed interview insights."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return result.get("summary", {}), result.get("evaluation", {}), result.get("feedback", "")
            
        except Exception as e:
            print(f"Error generating interview summary: {str(e)}")
            # Return minimal default values in case of error
            return (
                {"key_points": ["Interview completed"]}, 
                {"overall_impression": 5}, 
                "Thank you for participating in this interview."
            )
    
    def _get_system_prompt(self) -> str:
        """Generate the system prompt for the interview agent based on job details."""
        job_description_text = ""
        if self.job_description:
            job_description_text = f"\nJob Description: {self.job_description}"
            
        return f"""
        You are an AI-powered HR interviewer conducting a job interview for a {self.job_title} position at {self.company_name}.
        {job_description_text}
        
        Your task is to:
        1. Ask relevant, professional interview questions focused on this specific role
        2. Follow up on candidate responses to dig deeper into their experience and skills
        3. Assess technical knowledge, problem-solving abilities, and cultural fit
        4. Be conversational but professional, like a real HR interviewer
        5. Keep questions concise and clear
        
        This interview should have approximately {self.max_questions} questions total. 
        DO NOT mention that you're an AI unless directly asked.
        DO NOT ask multiple questions at once - ask one clear question at a time.
        DO NOT provide interview feedback during the conversation.
        """