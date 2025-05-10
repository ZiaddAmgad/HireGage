# HireGage API Documentation

## Overview

The HireGage API provides endpoints for conducting AI-powered job interviews. The API allows you to start interview sessions, process candidate responses, and generate interview summaries with evaluations.

## Base URL

```
https://api.hiregage.com/api/v1
```

For local development:
```
http://localhost:8000/api/v1
```

## Authentication

Most endpoints require API key authentication. Include your API key in the request header:

```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### System Endpoints

#### Health Check

```http
GET /system/health
```

Check the health status of the API.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": 1715385600,
  "environment": "production",
  "api_version": "0.1.0"
}
```

### Interview Endpoints

#### Start Interview

```http
POST /interview/start
```

Start a new interview session.

**Request Body**:
```json
{
  "job_title": "Software Engineer",
  "company_name": "Example Corp",
  "job_description": "We're looking for a skilled software engineer...",
  "interview_duration": 15
}
```

- `job_title`: Required. The job title for the interview.
- `company_name`: Optional. The company name.
- `job_description`: Optional. Detailed job description.
- `interview_duration`: Optional. Interview duration in minutes (default: 15).

**Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Hello, I'm your interviewer today. Can you tell me about your experience as a Software Engineer?"
}
```

#### Process Candidate Response

```http
POST /interview/{session_id}/respond
```

Process a candidate's response during the interview and get the next question.

**URL Parameters**:
- `session_id`: Required. The interview session ID.

**Request Body**:
```json
{
  "text": "I have 5 years of experience working as a software engineer...",
  "is_final": true
}
```

- `text`: Required. The candidate's spoken response.
- `is_final`: Optional. Whether this is the final transcription of this response (default: false).

**Response**:
```json
{
  "text": "That's great experience. Can you tell me about a challenging project you worked on?",
  "type": "text"
}
```

#### End Interview

```http
POST /interview/{session_id}/end
```

End the interview and generate a summary and evaluation.

**URL Parameters**:
- `session_id`: Required. The interview session ID.

**Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "job_title": "Software Engineer",
  "summary": {
    "key_points": [
      "5 years of experience in software development",
      "Expertise in JavaScript and Python",
      "Experience with team leadership"
    ]
  },
  "transcript": [
    {
      "role": "agent",
      "content": "Can you tell me about your experience?",
      "timestamp": 1715385600
    },
    {
      "role": "candidate",
      "content": "I have 5 years of experience...",
      "timestamp": 1715385630
    }
  ],
  "evaluation": {
    "technical_skills": 8,
    "communication": 7,
    "culture_fit": 8,
    "problem_solving": 7,
    "overall_impression": 8
  },
  "feedback": "The candidate demonstrated strong technical skills and communicated clearly..."
}
```

## Error Handling

The API uses standard HTTP status codes for error responses:

- `400` - Bad Request (Invalid input)
- `401` - Unauthorized (Authentication required)
- `403` - Forbidden (Insufficient permissions)
- `404` - Not Found (Resource not found)
- `422` - Unprocessable Entity (Validation error)
- `500` - Internal Server Error
- `503` - Service Unavailable (AI service error)

Error responses include a structured JSON body:

```json
{
  "message": "Error description",
  "type": "error_type",
  "detail": {}
}
```
