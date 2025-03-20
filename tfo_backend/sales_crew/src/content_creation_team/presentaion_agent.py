from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
from crewai import Task
load_dotenv()


class Slide(BaseModel):
    title: str
    content: str
    images: List[str]  
    testimonials: List[str]  

class PresentationOutput(BaseModel):
    topic: str
    slides: List[Slide] 

# Define the Agent properly
def presentation_designer() -> Agent:
    return Agent(
        role="Presesntation Designer",
        goal="Develop captivating PowerPoint decks for sales presentations.",
        verbose=True,
        tools=[SerperDevTool()],
        backstory=(
            "A visual storyteller who thrives in structuring information into compelling narratives through impactful slides."
        ),
        memory=True
    )

# Define the Task properly
def presentation_designer_task(agent: Agent) -> Task:
    return Task(
        description=
        """
        - Design a ten-slide PowerPoint deck that effectively showcases {topic} key features, benefits, and customer success stories.
        - Ensure the deck follows a professional, visually appealing format with structured slides (title, bullet points, images, testimonials).
        """,
        expected_output=
        """
        A well-structured PowerPoint deck for {topic} with ten slides, highlighting its unique selling points (USPs), benefits, and customer testimonials.
        """,
        agent=agent ,
        output_pydantic=PresentationOutput
    )

# Define the Crew properly
def create_crew() -> Crew:
    """Creates the Crew with the agent and task"""
    agent = presentation_designer()
    task = presentation_designer_task(agent)

    return Crew(
        agents=[agent],   
        tasks=[task],    
        process=Process.sequential,
        verbose=True,
    )


 

from asgiref.sync import sync_to_async
def run_chatbot(history):
    print("run_chatbot of presentation reached")


    inputs = {"topic": history}

    try:
        # Create crew
        crew = create_crew()

        # Execute crew logic
        result = crew.kickoff(inputs=inputs)

        # Validate result
        if result is None:
            raise ValueError("Crew execution returned None.")

        return str(result)

    except Exception as e:
   
        print(f"An error occurred: {e}")
        return {"error": f"Error processing message: {str(e)}"}