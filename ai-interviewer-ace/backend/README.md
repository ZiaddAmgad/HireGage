# HireGage Backend

This is the FastAPI backend for the HireGage AI HR Interview Agent. It provides the API endpoints and AI logic for conducting automated job interviews.

## Features

- FastAPI-based REST API
- AI-powered interview agent using OpenAI's GPT models
- Customizable interview content based on job titles and descriptions
- Real-time interview processing
- Interview summary and candidate evaluation
- Structured response formatting

## Architecture

The backend is organized into several components:

- `app/main.py`: Application entry point and FastAPI initialization
- `app/agent_logic.py`: Interview agent core logic
- `app/routers/`: API endpoints organized by feature
- `app/middleware/`: Custom middleware for logging, error handling, etc.
- `app/schemas/`: Pydantic models for request/response validation
- `app/models/`: Database models (SQLAlchemy)
- `app/utils/`: Utility functions and helpers

## Setup Instructions

### Prerequisites

- Python 3.10+
- OpenAI API key
- Supabase account (for storage and realtime features)

### Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Copy the `.env.example` file to `.env` and update with your own values:
     ```bash
     cp .env.example .env
     ```
   - Edit the `.env` file with your configuration:
     ```
     # API Settings
     API_VERSION=v1
     API_PREFIX=/api/v1
     DEBUG=True

     # Security
     SECRET_KEY=your_secret_key_for_jwt
     ACCESS_TOKEN_EXPIRE_MINUTES=30

     # OpenAI API
     OPENAI_API_KEY=your_openai_api_key
     OPENAI_MODEL=gpt-4o     # Supabase
     SUPABASE_URL=your_supabase_url
     SUPABASE_KEY=your_supabase_key
     ```

## Running the Server

### Development Mode

Run the server with hot-reload for development:

```bash
python run.py --env dev
```

Or use uvicorn directly:

```bash
uvicorn app.main:app --reload
```

### Production Mode

For production deployment:

```bash
python run.py --env prod
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc docs: http://localhost:8000/redoc

## API Endpoints

### System Endpoints
- `GET /` - Welcome message and API info
- `GET /api/v1/system/health` - Health check endpoint
- `GET /api/v1/system/info` - System information (debug mode only)

### Interview Endpoints
- `POST /api/v1/interview/start` - Start a new interview session
- `POST /api/v1/interview/{session_id}/respond` - Process candidate's response
- `POST /api/v1/interview/{session_id}/end` - End interview and get summary/evaluation

For detailed API documentation, see [API Documentation](docs/api_documentation.md).

## Testing

Run tests with pytest:

```bash
pytest
```

Run with coverage report:

```bash
pytest --cov=app tests/
```

## License

Copyright © 2025 HireGage