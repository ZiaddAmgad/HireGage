"""
Test utilities and mocks for HireGage backend testing
"""

# Mock responses for OpenAI API
MOCK_OPENAI_RESPONSES = {
    "initial_greeting": {
        "choices": [
            {
                "message": {
                    "content": "Hello! I'm your interviewer today for the Software Engineer position at Tech Corp. Could you start by telling me about your relevant experience in software development?"
                }
            }
        ]
    },
    "follow_up": {
        "choices": [
            {
                "message": {
                    "content": "That's great background. Could you tell me about a challenging technical problem you've solved in your previous role?"
                }
            }
        ]
    },
    "summary": {
        "choices": [
            {
                "message": {
                    "content": '{"summary": {"key_points": ["5 years experience", "Worked with Python/React", "Led a team of 3"]}, "evaluation": {"technical_skills": 8, "communication": 7, "culture_fit": 8, "problem_solving": 7, "overall": 7.5}, "feedback": "Strong technical skills with good communication. Consider providing more specific examples of problem-solving."}'
                }
            }
        ]
    }
}

# Mock interview transcript
MOCK_TRANSCRIPT = [
    {"role": "assistant", "content": "Hello! I'm your interviewer today for the Software Engineer position at Tech Corp. Could you start by telling me about your relevant experience in software development?", "timestamp": 1651234567.0},
    {"role": "candidate", "content": "I have been a software developer for 5 years, primarily working with Python and React. In my most recent role, I led a team of 3 developers working on a customer-facing web application.", "timestamp": 1651234587.0},
    {"role": "assistant", "content": "That's great background. Could you tell me about a challenging technical problem you've solved in your previous role?", "timestamp": 1651234607.0}
]
