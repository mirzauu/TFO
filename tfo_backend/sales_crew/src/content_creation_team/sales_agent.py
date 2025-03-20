from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
import logging
import asyncio

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(filename='sales_agent.log', level=logging.ERROR)

# Validate environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")
if not openai_api_key or not serper_api_key:
    raise ValueError("Required environment variables are not set.")

# Define the Agent
def sales_brochure_specialist() -> Agent:
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=1000,
        api_key=openai_api_key
    )
    serper_tool = SerperDevTool(api_key=serper_api_key)
    
    return Agent(
        role="Sales Brochure Strategist & Designer",
        goal="Craft high-converting, visually stunning sales brochures that captivate audiences and drive engagement.",
        verbose=True,
        tools=[serper_tool],
        backstory=(
            "With years of experience in marketing and design, you have a keen eye for aesthetics "
            "and an in-depth understanding of persuasive messaging. Your expertise lies in crafting "
            "brochures that not only look stunning but also effectively communicate value, evoke emotions, "
            "and inspire action. Whether it's a sleek corporate brochure or a vibrant product showcase, "
            "your designs always strike the perfect balance between form and function."
        ),
        memory=True,
        llm=llm
    )
from pydantic import BaseModel
from typing import List

class SalesBrochure(BaseModel):
    response: str  # e.g., "Sales brochure created", "Modifications applied"
    brochure: str  # Structured content of the sales brochure

# Define the Task
# Define the Task
def sales_brochure_specialist_task(agent: Agent) -> Task:
    return Task(
        description="""
        **User Input:** {topic}  
        **Conversation History:** {history}  

        ## **Task Overview**  
        Analyze the user's input and conversation history to determine the appropriate response type for creating or modifying a sales brochure.

        ### **Guidelines for Structuring the Brochure**  
        The brochure should follow this structured format for clarity and professionalism:

        **1. Title**  
        - A compelling, attention-grabbing title that clearly defines the brochure’s purpose.

        **2. Introduction**  
        - A short and engaging introduction that sets the tone and communicates the core message.

        **3. Key Sections**  
        *a. Product/Service Overview*  
        - Concise details on the product/service, including its purpose and target audience.

        *b. Features & Benefits*  
        - Clearly highlight the main features and their advantages.
        - Example:
            - **Feature 1:** Brief explanation of its benefit.
            - **Feature 2:** How it solves user pain points.

        *c. Testimonials & Social Proof*  
        - Real customer feedback or case studies to build credibility.

        *d. Call to Action (CTA)*  
        - A clear directive encouraging users to take action (e.g., "Contact us now!", "Get your free trial today!").

        **4. Design Elements**  
        - Ensure visually appealing layout and branding consistency.
        - Maintain readability with high-quality images and structured formatting.

        ### **How to Respond Based on User Requests**  
        1. **If it's an initial request or a complete brochure request:**  
        - Generate a fully structured sales brochure following the format above.

        2. **If it's a follow-up question or a request to modify a specific section:**  
        - Only modify the requested part while keeping the existing structure intact.

        3. **If the request requires clarification:**  
        - Ask specific questions to understand what changes or additions are needed.

        ## **Important Note**  
        - Use the **Serper tool only for generating new brochures**, not for editing existing ones.
        """,
        expected_output="""
        **Final Expected Output:**  
        A professional, structured, and market-ready sales brochure following the defined format.  

        - The output should be formatted properly for both **digital distribution and print-ready use**.  
        - If clarification is needed, a follow-up question should be provided instead.  
        """,
        agent=agent,
        output_pydantic=SalesBrochure
    )


# Define the Crew
def create_crew() -> Crew:
    agent = sales_brochure_specialist()
    task = sales_brochure_specialist_task(agent)
    return Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )


from organizations.models import ChatMessage
from asgiref.sync import sync_to_async
def run_chatbot(topic,history,id):
    print("run_chatbot reached", history)
    
    # Validate and clean history
    cleaned_history = []
    for entry in history:
        if isinstance(entry.get("content"), str):  # Ensure content is a string
            cleaned_history.append(entry)
        else:
            logging.warning(f"Malformed history entry skipped: {entry}")

    # # Construct history string
    history_str = "\n".join([f"{entry['role']}: {entry['content']}" for entry in cleaned_history])
    inputs = {"topic": topic,"history":history_str}

 
        # Create crew
    crew = create_crew()

    # Execute crew logic
    result = crew.kickoff(inputs=inputs)
       # Check if the result is a CrewOutput object
    print("Crew Output:", result)

# Attempt to convert the result to a dictionary if possible
    if hasattr(result, "to_dict"):  
        result_dict = result.to_dict()  # Convert CrewOutput-like object to a dictionary
        print("Converted CrewOutput to dict:", result_dict)  # Debugging

        # Ensure expected keys exist
        if "response" in result_dict and "brochure" in result_dict:
            parsed_result = SalesBrochure(**result_dict)  
            
            return str(parsed_result.brochure)
        else:
            raise ValueError(f"Missing expected keys in CrewOutput: {result_dict.keys()}")

    elif isinstance(result, dict):  # If result is already a dictionary
        parsed_result = SalesBrochure(**result)
        return str(parsed_result.brochure)

    elif isinstance(result, SalesBrochure):  # If result is already the correct Pydantic model
        return str(result.brochure)

    else:
        raise ValueError(f"Unexpected output format: {type(result)}")