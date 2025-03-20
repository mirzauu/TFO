import asyncio
import logging
from pymongo import MongoClient
from organizations.models import ChatMessage
from marketing_crew.src.seo_sem_crew.chatcrew import SeoSemCrew
from marketing_crew.src.seo_sem_crew.config import (
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
   
    crew_instance = SeoSemCrew()
   

    task_mapping = {
    AgentType.KEYWORD_RESEARCH_TASK: "keyword_research_task",
    AgentType.CONTENT_OPTIMIZATION_TASK: "content_optimization_task",
    AgentType.BACKLINK_ANALYSIS_TASK: "backlink_analysis_task",
    AgentType.ANALYTICS_MONITORING_TASK: "analytics_monitoring_task",
    AgentType.SEO_REPORTING_TASK: "seo_reporting_task",
    AgentType.AD_COPY_TASK: "ad_copy_task",
    AgentType.SEM_CAMPAIGN_MANAGEMENT_TASK: "sem_campaign_management_task",
    AgentType.COMPETITOR_ANALYSIS_TASK: "competitor_analysis_task",
    AgentType.SEO_AUDIT_TASK: "seo_audit_task",
    AgentType.INTERNAL_LINKING_TASK: "internal_linking_task",
    AgentType.CONTENT_STRATEGY_TASK: "content_strategy_task",
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

        AgentType.KEYWORD_RESEARCH_TASK: ("Analysis report", "details", "response"),
        AgentType.CONTENT_OPTIMIZATION_TASK: ("Analysis report", "details", "response"),
        AgentType.BACKLINK_ANALYSIS_TASK: ("Analysis report", "details", "response"),
        AgentType.ANALYTICS_MONITORING_TASK: ("competitor analyst", "details", "response"),
        AgentType.SEO_REPORTING_TASK:("sales pitch", "details", "response"),
        AgentType.AD_COPY_TASK: ("Analysis report", "details", "response"),
        AgentType.SEM_CAMPAIGN_MANAGEMENT_TASK: ("Analysis report", "details", "response"),
        AgentType.COMPETITOR_ANALYSIS_TASK: ("Analysis report", "details", "response"),
        AgentType.SEO_AUDIT_TASK: ("competitor analyst", "details", "response"),
        AgentType.INTERNAL_LINKING_TASK: ("posts", "posts", "response"),
        AgentType.CONTENT_STRATEGY_TASK:("Analysis report", "details", "response"),
       
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
