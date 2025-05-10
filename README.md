# HireGage

## AI HR Interview Agent

An AI-powered virtual HR agent that conducts interview-style conversations based on a user's job title, helping assess role fit and gather candidate insights automatically.

## Project Overview

HireGage is a sophisticated AI interview platform that simulates real HR interviews, providing:

- Customized interviews based on job title and company
- Real-time conversation with natural follow-up questions
- Comprehensive post-interview evaluation and insights
- Transcript recording for later review

## Project Structure

- **Backend**: FastAPI-based API with OpenAI integration
  - Interview agent logic
  - API endpoints
  - Configuration management
  
- **Frontend**: React/TypeScript web application
  - Video/audio interface
  - Real-time transcription
  - Interactive UI components

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd ai-interviewer-ace/backend
   ```

2. Follow the setup instructions in the backend README.

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd ai-interviewer-ace/frontend
   ```

2. Follow the setup instructions in the frontend README.

## Technologies Used

- **Backend**: Python, FastAPI, OpenAI API, Supabase
- **Frontend**: React, TypeScript, Tailwind CSS, WebRTC
- **Data Storage**: Supabase

## Features

- Real-time audio/video interview interface
- Customizable interview questions based on job role
- Automatic transcription of responses
- Interview summary and candidate evaluation
- Score-based assessment of technical and soft skills
