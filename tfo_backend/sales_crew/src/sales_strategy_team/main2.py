import sys
import warnings

from sales_crew.src.sales_strategy_team.manager import SalesStrategyTeam
from organizations.models import ChatMessage
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
import json
from django.shortcuts import get_object_or_404

import re
from pymongo import MongoClient

from tfo_backend.mongodb import chat_collection,db


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
 
    inputs = {
        'topic':'',
        'human_task': f"{message}",
        "context":message_dict
    }
    result=SalesStrategyTeam().crew().kickoff(inputs=inputs)
    return str(result)
