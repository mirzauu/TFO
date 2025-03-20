import asyncio
import logging
from pymongo import MongoClient
from organizations.models import ChatMessage
from marketing_crew.src.social_media_crew.chatcrew import SocialMediaCrew
from marketing_crew.src.social_media_crew.config import (
    
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
   
    crew_instance = SocialMediaCrew()


    task_mapping = {
        AgentType.COMPETITOR_ANALYSIS_TASK_TASK : "competitor_analysis_task",
        AgentType.CONTENT_PLANNER_TASK : "content_planner_task",
        AgentType.BRAND_MONITOR_TASK : "brand_monitor_task",
        AgentType.INFLUENCER_SCOUT_TASK :"influencer_scout_task",
        AgentType.CUSTOMER_ENGAGEMENT_TASK : "customer_engagement_task",
        AgentType.METRICS_ANALYST_TASK:"metrics_analyst_task",
        AgentType.HASHTAG_STRATEGY_TASK:"hashtag_strategy_task",
        AgentType.CAMPAIGN_DESIGN_TASK:"campaign_design_task",
        AgentType.CAPTION_CREATION_TASK:"caption_creation_task",
        AgentType.SCRIPTING_CREATION_TASK:"scriptwriting_task"
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

        AgentType.COMPETITOR_ANALYSIS_TASK_TASK :  ("competitor analyst", "details", "response"),
        AgentType.CONTENT_PLANNER_TASK :  ("sales pitch", "details", "response"),
        AgentType.BRAND_MONITOR_TASK :  ("competitor analyst", "details", "response"),
        AgentType.INFLUENCER_SCOUT_TASK : ("posts", "posts", "response"),
        AgentType.CUSTOMER_ENGAGEMENT_TASK :  ("email templates", "templates", "response"),
        AgentType.METRICS_ANALYST_TASK: ("Analysis report", "details", "response"),
        AgentType.HASHTAG_STRATEGY_TASK: ("email templates", "templates", "response"),
        AgentType.CAMPAIGN_DESIGN_TASK: ("discription", "descriptions", "response"),
        AgentType.CAPTION_CREATION_TASK: ("discription", "descriptions", "response"),
        AgentType.SCRIPTING_CREATION_TASK: ("discription", "descriptions", "response"),
       
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
