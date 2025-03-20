from crewai import Agent, LLM
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the API key
API_KEY = os.getenv("OPENAI_API_KEY")


openapi_llm = LLM(
    model="gpt-3.5-turbo",
    temperature=0.7,
    base_url="https://api.openai.com/v1",
    api_key=API_KEY
)
