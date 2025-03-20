import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from pymongo import MongoClient
from channels.db import database_sync_to_async
from django.http import JsonResponse
from bson.objectid import ObjectId
from pymongo import DESCENDING,ASCENDING
import asyncio

from tfo_backend.mongodb import chat_collection,db

@database_sync_to_async
def send_form_to_view(message_id, form_data):
    """
    Call the Django view function with the message_id and form data.
    """
    from organizations.crew_handler import handle_crew_view  # Replace with your app name
    response = handle_crew_view(message_id, form_data)
    return response

@database_sync_to_async
def send_message_to_view(message,message_id):
    """
    Call the Django view function with the message_id and form data.
    """
    print("aawwwwwwaaaaaaaa",message,message_id)
    from organizations.crew_handler import handle_crew_manual_view  # Replace with your app name
    response = handle_crew_manual_view(message,message_id)
    return response
@database_sync_to_async
def send_retry_to_view(message_id):
    """
    Call the Django view function with the message_id and form data.
    """
    from organizations.crew_handler import handle_crew_retry_view  # Replace with your app name
    response = handle_crew_retry_view(message_id)
    return response

class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.message_id = self.scope['url_route']['kwargs']['id']
        self.room_group_name = f"message_{self.message_id}"

        # Join the WebSocket room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the WebSocket room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Parse received message
        data = json.loads(text_data)
        action = data.get('action')

        if action == "fetch_messages":
            messages = await self.get_messages()
            await self.send(text_data=json.dumps({
                "action": "show_messages",
                "messages": messages,
            }))
        elif action == "form":
            from organizations.tasks import process_form_task
            form_data = data.get('form')
            if not form_data:
                await self.send(text_data=json.dumps({
                    "action": "error",
                    "error": "No form data provided."
                }))
                return

            message_id = self.message_id
            task = process_form_task.delay(message_id, form_data)  # Send to Celery

            # await self.send(text_data=json.dumps({
            #     "action": "task_queued",
            #     "message": "Agent is Working",
            #     "user": "AI"
            # }))

        elif action == "chat_manually":
            from organizations.tasks import process_chat_task
            message = data.get('message')
            if not message:
                await self.send(text_data=json.dumps({
                    "action": "error",
                    "error": "No message data provided."
                }))
                return 

            message_id = self.message_id
            task = process_chat_task.delay(message_id, message)  # Send to Celery

            await self.send(text_data=json.dumps({
                "action": "task_queued",
                "message": "We are working on it",
                "user": "AI"
            }))
            # Wait for 3 seconds
            await asyncio.sleep(3)

            # Send follow-up response
            await self.send(text_data=json.dumps({
                "action": "task_queued",
                "message": "Manager agent is reviewing",
                "user": "AI"
            }))
        elif action == "retry":
            from organizations.tasks import process_retry_task
            message_id = self.message_id

            task = process_retry_task.delay(message_id)  # Send task to Celery queue

            await self.send(text_data=json.dumps({
                "action": "task_queued",
                "message": "Agent is Working",
                "user": "AI" 
            }))


    async def chat_message(self, event):
        """
        Handle the `chat.message` event.
        """
        await self.send(text_data=json.dumps({
            "action": "new_message",
            "message": event["message"],
        }))      

    async def get_messages(self):
        """
        Fetch all messages for the current session from MongoDB.
        """
        messages = []
        try:
            message_documents = chat_collection.find({"chat_message_id": str(self.message_id)}).sort("message_number", 1) # Ensure sorting by timestamp in descending order
            print(message_documents)
            messages = []
            for doc in message_documents:
        
                # Convert ObjectId and datetime fields to JSON serializable format
                cleaned_doc = {}
                for key, value in doc.items():
                    if isinstance(value, ObjectId):
                        cleaned_doc[key] = str(value)  # Convert ObjectId to string
                    elif isinstance(value, datetime):
                        cleaned_doc[key] = value.isoformat()  # Convert datetime to string
                    else:
                        cleaned_doc[key] = value  # Keep other values as they are

                messages.append(cleaned_doc)
            print(messages)    


        except Exception as e:
            print(f"Error fetching messages: {e}")
        return messages