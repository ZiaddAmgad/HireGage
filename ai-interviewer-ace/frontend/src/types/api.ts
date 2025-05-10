// Type definitions for API requests and responses

export interface JobTitleRequest {
  job_title: string;
  company_name?: string;
  job_description?: string;
  interview_duration?: number;
}

export interface CandidateResponse {
  text: string;
  is_final: boolean;
}

export interface AgentMessage {
  text: string;
  type?: string;
}

export interface InterviewResponse {
  session_id: string;
  message: string;
}

export interface InterviewSummary {
  session_id: string;
  job_title: string;
  summary: {
    key_points: string[];
  };
  transcript: Array<{
    role: string;
    content: string;
    timestamp: number;
  }>;
  evaluation: {
    technical_skills: number;
    communication: number;
    culture_fit: number;
    problem_solving: number;
    overall_impression: number;
  };
  feedback: string;
}
