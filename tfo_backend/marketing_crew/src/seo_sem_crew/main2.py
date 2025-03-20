#!/usr/bin/env python
import sys
import warnings
from marketing_crew.src.seo_sem_crew.manager import SeoSemCrew
from django.shortcuts import get_object_or_404
from organizations.models import ChatMessage

import re

from tfo_backend.mongodb import chat_collection,db


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run(message_id,message):
    chat_message = get_object_or_404(ChatMessage, id=message_id)
    messages = list(chat_collection.find({"chat_message_id": str(message_id)}))
    print("nn",message)

    message_dict = {"user": [], "AI": []}

    for msg in messages:
        try:
            msg["_id"] = str(msg["_id"])  # Convert ObjectId to string
            message_dict[msg["user"]].append(msg["message"])  # Append message
        except KeyError:
            print(messages)

    print(message_dict)
    """
    Run the crew.
    """
    inputs = inputs = {
        
        'website_name': "",
        'competitors': "", 
        'target_audience': " ",
        'ad_budget': "",
        'primary_goals': "",
        'current_year': "",
        "human_task": f"{message}",
        "context":message_dict

    }
    result=SeoSemCrew().crew().kickoff(inputs=inputs)
    return str(result)
