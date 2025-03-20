from enum import Enum
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, ValidationError
import instructor
from openai import AsyncOpenAI
import os
import asyncio
import logging
import re
from chat.classification_prompt import CLASSIFIER_PROMPTS
# Configure logging
logging.basicConfig(level=logging.INFO)
from chat.llm_config import call_llm_with_structured_output,get_llm_response
# Load environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

# Initialize OpenAI client
client = AsyncOpenAI(api_key=api_key)
structured_client = instructor.from_openai(client, mode=instructor.Mode.JSON)

# Enums and Pydantic Models
class ClassificationResult(Enum):
    LLM_SUFFICIENT = "LLM_SUFFICIENT"
    AGENT_REQUIRED = "AGENT_REQUIRED"

class AgentType(Enum):
    SALES_BROCHURE_SPECIALIST = "sales_brochure_specialist"
    EMAIL_TEMPLATE_CREATOR = "email_template_creator"
    PRODUCT_DESCRIPTION_WRITER = "product_description_writer"
    PRESENTATION_DESIGNER = "presentation_designer"
    SOCIAL_MEDIA_CONTENT_CREATOR = "social_media_content_creator"

class ClassificationResponse(BaseModel):
    classification: ClassificationResult
    required_agent: Optional[AgentType] = None
    formatted_prompt: str  # New field for the formatted prompt

class QueryClassifier:
    @staticmethod
    async def classify_query(query: str, history: List[Dict[str, str]]) -> ClassificationResponse:
        print("Reached classify_query method", history)

        # Domain selection (Hardcoded for now)
        domain = "content_creation"
        if domain not in CLASSIFIER_PROMPTS:
            raise ValueError(f"Unsupported domain: {domain}")

        # Load the prompt (Fixed KeyError)
        prompt_template = CLASSIFIER_PROMPTS[domain]

        # Validate history format (Simplified)
        if not all(isinstance(msg, dict) and "role" in msg and "content" in msg for msg in history):
            raise ValueError("Invalid history format. Expected a list of dictionaries with 'role' and 'content' keys.")

        # Extract query and history from the last user message
        last_message = history[-1]["content"]
        match = re.search(r"Query:\s*(.*?)\nHistory:\n(.*)", last_message, re.DOTALL)

        if match:
            query = match.group(1).strip()
            raw_history = match.group(2).strip()

            # Extract history maintaining separate role-content pairs
            extracted_history = []
            for line in raw_history.split("\n"):
                if line.startswith("User: "):
                    extracted_history.append({"role": "user", "content": line[len("User: "):]})
                elif line.startswith("Assistant: "):
                    extracted_history.append({"role": "assistant", "content": line[len("Assistant: "):]})

        else:
            extracted_history = history

        # Prepare structured message history
        messages = [{"role": "system", "content": prompt_template}] + extracted_history

        # Append the latest user query as a separate message
        messages.append({"role": "user", "content": query})

        print("message", messages)

        # Call LLM function
        return await call_llm_with_structured_output(messages, ClassificationResponse)
def get_content_creation_messages(query: str, history: List[str]) -> List[dict]:
    """
    Prepares the messages for the Content Creation Manager LLM.
    """
    return [
        {"role": "system", "content": "You are a Content Creation Manager. You handle any task related to content creation like sales brochure creation, email template creation, product description writing, and designing."},
        {"role": "user", "content": f"Query: {query}\nHistory: {history[-5:]}"}
    ]

async def call_content_creation_manager(query: str, history: List[str], model_name: str = "gpt-4o") -> str:
    """
    Calls the Content Creation Manager LLM with a given query and history.
    """
    messages = get_content_creation_messages(query, history)
    return await get_llm_response(model_name, messages)