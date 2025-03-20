from enum import Enum
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, ValidationError
import instructor
from openai import AsyncOpenAI
import os
import asyncio
import logging
from chat.classification_prompt import CLASSIFIER_PROMPTS
from chat.system_prompt import SYSTEM_PROMPT
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
    COMPETITOR_ANALYSIS_TASK_TASK = "competitor_analysis_task"
    CONTENT_PLANNER_TASK = "content_planner_task"
    BRAND_MONITOR_TASK = "brand_monitor_task"
    INFLUENCER_SCOUT_TASK = "influencer_scout_task"
    CUSTOMER_ENGAGEMENT_TASK = "customer_engagement_task"
    METRICS_ANALYST_TASK="metrics_analyst_task"
    HASHTAG_STRATEGY_TASK="hashtag_strategy_task"
    CAMPAIGN_DESIGN_TASK="campaign_design_task"
    CAPTION_CREATION_TASK="caption_creation_task"
    SCRIPTING_CREATION_TASK="scriptwriting_task"

class ClassificationResponse(BaseModel):
    classification: ClassificationResult
    required_agent: Optional[AgentType] = None
    formatted_prompt: str 

class QueryClassifier:
    @staticmethod
    async def classify_query(query: str, history: List[Dict[str, str]]) -> ClassificationResponse:
        print("Reached classify_query method")

        # Domain selection (Hardcoded for now)
        domain = "social_media"
        if domain not in CLASSIFIER_PROMPTS:
            raise ValueError(f"Unsupported domain: {domain}")

        # Load the prompt (Fixed KeyError)
        prompt_template = CLASSIFIER_PROMPTS[domain]

        # Validate history format (Simplified)
        if not all(isinstance(msg, dict) and "role" in msg and "content" in msg for msg in history):
            raise ValueError("Invalid history format. Expected a list of dictionaries with 'role' and 'content' keys.")

        # Prepare inputs (Fixed string formatting)
        formatted_history = "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in history[-5:])
        messages = [
            {"role": "system", "content": prompt_template},
            {"role": "user", "content": f"Query: {query}\nHistory:\n{formatted_history}"},
        ]

        # Call LLM function
        return await call_llm_with_structured_output(messages, ClassificationResponse)
    

def get_content_creation_messages(query: str, history: List[str]) -> List[dict]:
    """
    Prepares the messages for the Content Creation Manager LLM.
    """
    domain = "social_media"
    prompt_template = SYSTEM_PROMPT[domain]

    return [
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": f"Query: {query}\nHistory: {history[-5:]}"}
    ]

async def call_content_creation_manager(query: str, history: List[str], model_name: str = "gpt-4o") -> str:
    """
    Calls the Content Creation Manager LLM with a given query and history.
    """
    messages = get_content_creation_messages(query, history)
    return await get_llm_response(model_name, messages)