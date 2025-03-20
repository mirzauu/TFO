import asyncio
import logging
from pymongo import MongoClient
from organizations.models import ChatMessage
from sales_crew.src.content_creation_team.chatcrew import ContentCreationTeam
from sales_crew.src.content_creation_team.classification import (
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


def get_chat_message(message_id):
    """Retrieve a ChatMessage object by ID."""
    return ChatMessage.objects.filter(id=message_id).first()


async def fetch_chat_history(message_id):
    """
    Fetch and format chat history from MongoDB.
    """
    try:
        messages = list(chat_collection.find({"chat_message_id": str(message_id)}))
        if not messages:
            logging.warning(f"No chat history found for message ID: {message_id}")
            return []

        # Format history for processing
        formatted_history = []
        for msg in messages[-20:]:
            try:
                role = msg["user"] if msg["user"] == "user" else "assistant"
                formatted_history.append({"role": role, "content": msg["message"]})
            except KeyError:
                logging.error(f"Malformed message encountered: {msg}")
        return formatted_history
    except Exception as e:
        logging.error(f"Error fetching chat history: {e}")
        return []


async def process_agent_response(agent_type, formatted_prompt):
    """
    Process the response based on the required agent type.
    """
    crew_instance = ContentCreationTeam()
    selected_tasks = []

    task_mapping = {
        AgentType.SALES_BROCHURE_SPECIALIST: ("sales_brochure_specialist_task", "brochure"),
        AgentType.PRESENTATION_DESIGNER: ("presentation_designer_task", "slides"),
        AgentType.EMAIL_TEMPLATE_CREATOR: ("email_template_creator_task", "email templates"),
        AgentType.PRODUCT_DESCRIPTION_WRITER: ("product_description_writer_task", "description"),
        AgentType.SOCIAL_MEDIA_CONTENT_CREATOR: ("social_media_content_creator_task", "posts"),
    }

    task_name, output_format = task_mapping.get(agent_type, (None, None))

    if task_name:
        task_func = getattr(crew_instance, task_name, None)
        if task_func:
            selected_tasks.append(task_func())
        crew = crew_instance.crew()
        crew.tasks = selected_tasks
        result = crew.kickoff(inputs={"topic": formatted_prompt})
        output = result.to_dict()

        content_key = task_mapping[agent_type][0].replace("_task", "")
        content = output.get(content_key, "No response available")
        message = output.get("response", f"No {output_format} available")

        return output_format, content, message
    else:
        logging.error(f"Unknown agent type: {agent_type}")
        return None, None, "Error: Unknown agent type."


async def run(d, message):
    """
    Main function to process a chat message and generate a response.
    """
    try:
        message_id = d
        logging.info(f"Processing message ID: {message_id}, Message: {message}")

        # Fetch and format chat history
        history_formatted = await fetch_chat_history(message_id)

        # Classify the query
        classification_response = await QueryClassifier.classify_query(
            query=message, history=history_formatted
        )
        logging.info(f"Classification result: {classification_response.classification}")
        logging.info(f"Required agent type: {classification_response.required_agent}")

        if classification_response.classification == ClassificationResult.AGENT_REQUIRED:
            formatted_prompt = classification_response.formatted_prompt
            required_agent = classification_response.required_agent

            # Process the response based on the required agent
            output_format, content, message = await process_agent_response(
                required_agent, formatted_prompt
            )
        else:
            logging.info("Query classified as LLM_SUFFICIENT.")
            message = await call_content_creation_manager(message, history_formatted)
            output_format = "text"
            content = None

        # Ensure message is JSON-serializable
        if isinstance(message, BaseModel):  # If result is a Pydantic model
            message = message.dict()  # Convert to dictionary
        elif not isinstance(message, str):  # Handle unexpected types
            logging.warning(f"Unexpected result type: {type(message)}. Converting to string.")
            output_format = "text"
            message = str(message)

        return message, output_format, content

    except Exception as e:
        logging.error(f"Error processing message: {e}")
        return {"error": f"Error processing message: {str(e)}. Start a new chat to continue."}