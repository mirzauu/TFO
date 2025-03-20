#!/usr/bin/env python
import sys
import warnings

from sales_crew.src.content_creation_team.manager import ContentCreationTeam
from organizations.models import ChatMessage
import json
from django.shortcuts import get_object_or_404


from tfo_backend.mongodb import chat_collection,db

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run(message_id,message):
    chat_message = get_object_or_404(ChatMessage, id=message_id)
    messages = list(chat_collection.find({"chat_message_id": str(message_id)}))
    print("nn",message)

    history = messages[-20:] 
    message_dict = {"user": [], "AI": []}
    for msg in history:
        try:
            msg["_id"] = str(msg["_id"])  # Convert ObjectId to string
            message_dict[msg["user"]].append(msg["message"])  # Append message
        except KeyError:
            print(messages)

    last_messages = messages[-2:]  # Get the last two messages
    last_message_dict = {"user": [], "AI": []}
    for msg in last_messages:
        try:
            msg["_id"] = str(msg["_id"])  # Convert ObjectId to string
            last_message_dict[msg["user"]].append(msg["message"])
        except KeyError:
            print(last_messages)        
 
    inputs = {
            'product_description': '',
            'brand_tone': '',
            'target_audience': '',
            'distribution_format': '',
            'topic': '',
            'chat_message_id': chat_message.id,
            'human_task': message,
            "context": message_dict,
            "last_conversation": last_message_dict
        }
    result=ContentCreationTeam().crew().kickoff(inputs=inputs)
    return str(result)

 