from enum import Enum
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, ValidationError
import instructor
from openai import AsyncOpenAI
import os
import asyncio
import logging
from chat.classification_prompt import CLASSIFIER_PROMPTS
# Configure logging
logging.basicConfig(level=logging.INFO)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

# Initialize OpenAI client
client = AsyncOpenAI(api_key=api_key)
structured_client = instructor.from_openai(client, mode=instructor.Mode.JSON)
# Function to Call LLM with Structured Output
async def call_llm_with_structured_output(messages: List[dict], output_schema: BaseModel, size: str = "small") -> Any:
    try:
        logging.info("Calling LLM with structured output...")
        response = await structured_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=150,
            response_model=output_schema,
        )
        logging.info("LLM response received successfully.")
        return output_schema(**response.model_dump())
    except ValidationError as e:
        logging.error(f"Validation error: {e}")
        raise
    except Exception as e:
        logging.error(f"Error during structured chat completion: {e}")
        raise



async def get_llm_response(model_name: str, messages: List[dict]) -> str:
    """
    Calls the LLM API with the specified model and messages.
    """
    try:
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=150,
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error during LLM call: {e}")
        raise