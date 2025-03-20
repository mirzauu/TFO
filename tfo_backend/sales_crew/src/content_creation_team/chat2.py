import asyncio
import logging
import json
from pymongo import MongoClient
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
from pydantic import BaseModel

from organizations.models import ChatMessage
from sales_crew.src.content_creation_team.chatcrew import ContentCreationTeam
from sales_crew.src.content_creation_team.classification import (
    QueryClassifier,
    ClassificationResponse,
    ClassificationResult,
    call_content_creation_manager,
    AgentType
)
from sales_crew.src.content_creation_team.sales_agent import run_chatbot as sales
from sales_crew.src.content_creation_team.presentaion_agent import run_chatbot as presentation

# Configure logging
logging.basicConfig(level=logging.INFO)

# MongoDB setup
MONGO_URI = "mongodb+srv://alimirsa123:a5VtspGwzNRv3m7b@cluster0.3wmvf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["tfo"]
chat_collection = db["chat"]

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
    crew_instance = ContentCreationTeam()
    task_mapping = {
        AgentType.SALES_BROCHURE_SPECIALIST: "sales_brochure_specialist_task",
        AgentType.PRESENTATION_DESIGNER: "presentation_designer_task",
        AgentType.EMAIL_TEMPLATE_CREATOR: "email_template_creator_task",
        AgentType.PRODUCT_DESCRIPTION_WRITER: "product_description_writer_task",
        AgentType.SOCIAL_MEDIA_CONTENT_CREATOR: "social_media_content_creator_task"
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
        AgentType.SALES_BROCHURE_SPECIALIST: ("brochure", "brochure", "response"),
        AgentType.PRESENTATION_DESIGNER: ("slides", "slides", "topic"),
        AgentType.EMAIL_TEMPLATE_CREATOR: ("email templates", "templates", "response"),
        AgentType.PRODUCT_DESCRIPTION_WRITER: ("description", "descriptions", "response"),
        AgentType.SOCIAL_MEDIA_CONTENT_CREATOR: ("posts", "posts", "response")
    }
    
    format_type, content_key, message_key = format_map.get(agent_type, ("text", "response", "response"))
    content = output.get(content_key, "No response available")
    message = output.get(message_key, "No response available")
    
    return message,format_type,content

async def run(d, message: str) -> tuple:
    """Process user query, classify it, and respond accordingly."""
    try:
        message_id = d
        logging.info(f"Processing message ID: {message_id}, Message: {message}")
        
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
