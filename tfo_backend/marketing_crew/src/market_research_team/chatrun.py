import asyncio
import logging
from pymongo import MongoClient
from organizations.models import ChatMessage
from marketing_crew.src.market_research_team.chatcrew import MarketResearchTeam
from marketing_crew.src.market_research_team.config import (
    QueryClassifier,
    ClassificationResponse,
    ClassificationResult,
    call_content_creation_manager,
    AgentType
)
from pydantic import BaseModel
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
from organizations.utilis import send_websocket_message
from tfo_backend.mongodb import chat_collection,db

def get_chat_message(message_id: int) -> ChatMessage:
    """Retrieve a chat message by its ID."""
    return ChatMessage.objects.filter(id=message_id).first()

def get_chat_history(message_id: int, limit: int = 20) -> list:
    """Retrieve and format chat history for a given message ID."""
    messages = list(chat_collection.find({"chat_message_id": str(message_id)}))[-limit:]
    history = []
    
    for msg in messages:
        try:
            role = "user" if msg.get("user") == "user" else "assistant"
            history.append({"role": role, "content": msg.get("message", "")})
        except KeyError:
            logging.error(f"Malformed message encountered: {msg}")
    
    return history

def process_agent_task(agent_type: AgentType, formatted_prompt: str) -> tuple:
    """Process the required agent task and return results."""
   
    crew_instance = MarketResearchTeam()
   

    task_mapping = {
    AgentType.REVIEW_ANALYST_TASK: "review_analyst_task",
    AgentType.SURVEY_DESIGNER_TASK: "survey_designer_task",
    AgentType.TREND_SPOTTER_TASK: "trend_spotter_task",
    AgentType.COMPETITOR_ANALYST_TASK: "competitor_analyst_task",
    AgentType.DEMOGRAPHIC_SPECIALIST_TASK: "demographic_specialist_task",
    AgentType.PERSONA_CREATOR_TASK: "persona_creator_task",
    AgentType.GEO_MARKET_ANALYST_TASK: "geo_market_analyst_task",
    AgentType.SENTIMENT_ANALYST_TASK: "sentiment_analyst_task",
    AgentType.GAP_ANALYST_TASK: "gap_analyst_task",
    AgentType.STRATEGIC_PLANNER_TASK: "strategic_planner_task",
}


 
    
    task_func_name = task_mapping.get(agent_type)
    if not task_func_name:
        logging.error("Unknown agent type.")
        return "error", "Unknown agent type.", "Error: Unknown agent type."
    
    task_func = getattr(crew_instance, task_func_name, None)
    if not task_func:
        logging.error(f"Task function {task_func_name} not found.")
        return "error", "Task function not found.", "Error: Task function not found."
    
    crew = crew_instance.crew()
    crew.tasks = [task_func()]
    result = crew.kickoff(inputs={"topic": formatted_prompt})
    output = result.to_dict()
    
    format_map = {

        AgentType.REVIEW_ANALYST_TASK: ("competitor analyst", "details", "response"),
        AgentType.SURVEY_DESIGNER_TASK: ("survey out", "details", "response"),
        AgentType.TREND_SPOTTER_TASK: ("Analysis report", "details", "response"),
        AgentType.COMPETITOR_ANALYST_TASK: ("competitor analyst", "details", "response"),
        AgentType.DEMOGRAPHIC_SPECIALIST_TASK: ("sales pitch", "details", "response"),
        AgentType.PERSONA_CREATOR_TASK: ("sales pitch", "details", "response"),
        AgentType.GEO_MARKET_ANALYST_TASK: ("Analysis report", "details", "response"),
        AgentType.SENTIMENT_ANALYST_TASK: ("Analysis report", "details", "response"),
        AgentType.GAP_ANALYST_TASK: ("competitor analyst", "details", "response"),
        AgentType.STRATEGIC_PLANNER_TASK: ("price report", "details", "response"),
       
    }
    
    format_type, content_key, message_key = format_map.get(agent_type, ("text", "response", "response"))
    content = output.get(content_key, "No response available")
    message = output.get(message_key, "No response available")
    
    return message,format_type,content

async def run(message_id, message: str) -> tuple:
    """Process user query, classify it, and respond accordingly."""
    try:
       
     
        # Retrieve chat history
        history = get_chat_history(message_id)
        
        # Classify the query
        response: ClassificationResponse = await QueryClassifier.classify_query(query=message, history=history)
        logging.info(f"Classification result: {response.classification}")
        
        # Determine action based on classification
        if response.classification == ClassificationResult.AGENT_REQUIRED:
            logging.info(f"Agent required: {response.required_agent}")
           
            return process_agent_task(response.required_agent, response.formatted_prompt)
        else:
            logging.info("Query classified as LLM_SUFFICIENT.")
            processed_message = await call_content_creation_manager(message, history)
            return processed_message,"text",None
    
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        return {"error": f"Error processing message: {str(e)}. Start a new chat to continue"}
