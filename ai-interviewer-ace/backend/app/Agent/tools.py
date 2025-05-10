from langchain.tools import tool






class Tools:

    @staticmethod
    @tool
    def ask_user(question: str) -> str:
        """Ask the user a question and wait for their answer.
         Call this function if you need more information from the user.
         Like introducing themselves or their experience.

        """
        print(f"🤖 (question): {question}")
        user_response = input("> You: ")
        return f'user answered:  {user_response}'
    

    @tool
    def get_interviewee_job_skills()->str:
        """Get the interviewee job skills."""
        return 'The interviewee has 5 years of experience in software development, working with Python and JavaScript. They have worked at XYZ Corp and ABC Inc.'


    @tool
    def create_an_mcq(question: str, options: list[str]) -> str:
        """Creates a multiple choice question for the interviewee.
        
        Args:
        
            question (str): The question to ask.
            options (list[str]): The options for the question.
        """
        print(f"🤖 (question): {question}")
        print(f"Options: {options}")
        user_response = input("> You: ")
        return f'user chose:  {user_response}'
    
    @tool
    def create_coding_problem(problem:str)->str:
        """Creates a coding problem for the interviewee.
        
        Args:
            problem (str): The coding problem to ask,provide a clear description of this.
        """
        print(f"🤖 (problem): {problem}")
        user_response = input("> You: ")
        return f'user solved:  {user_response}'
    
    @tool
    def send_interview_summary(summary:str)->str:
        """Sends the interview summary to the interviewee.
        
        Args:
            summary (str): The summary of the interview.
        """
        print(f"🤖 (summary): {summary}")
        user_response = input("> You: ")
        return f'user acknowledged:  {user_response}'

    @staticmethod
    def get_tools():
        """Get the list of tools."""
        return [
            # Tools.ask_user,
            Tools.get_interviewee_job_skills,
            Tools.create_an_mcq,
            Tools.send_interview_summary
        ]
