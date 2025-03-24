from celery import shared_task
import json
from django.http import JsonResponse
from organizations.consumers import send_retry_to_view,send_form_to_view, send_message_to_view  # Adjust the import path accordingly
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import asyncio
from django.core.cache import cache
from django.db import connection
from hr_crew.models import EmployeeDocuments
from celery.exceptions import SoftTimeLimitExceeded

@shared_task
def process_retry_task(message_id):
    # Clear cache
    cache.clear()

    # Ensure fresh database connection
    connection.close()

    # Fetch fresh count of EmployeeDocuments and print it
    count = EmployeeDocuments.objects.count()
    print(f"🔄 Updated EmployeeDocuments count: {count}")

    try:
        # Run async function inside a synchronous task
        response = asyncio.run(send_retry_to_view(message_id))

        # Convert response properly
        response_data = json.loads(response.content) if isinstance(response, JsonResponse) else response
    except Exception as e:
        response_data = {"error": f"Error processing form: {e}"}

    return response_data

@shared_task(soft_time_limit=10)  # Task will timeout after 10 seconds
def process_form_task(message_id, form_data):
    try:
        # Run async function inside Celery task
        response = asyncio.run(send_form_to_view(message_id, form_data))  

        # Convert response properly
        response_data = json.loads(response.content) if isinstance(response, JsonResponse) else response

    except SoftTimeLimitExceeded:
        response_data = {"error": "Task timed out! The process took too long."}
        
    except Exception as e:
        response_data = {"error": f"Error processing form: {e}"}

    return response_data

@shared_task(bind=True)
def process_chat_task(self, message_id, message):
    cache.clear()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Run async function safely inside Celery
        future = loop.create_task(send_message_to_view(message, message_id))

        # Ensure Celery can enforce time limits
        response = loop.run_until_complete(asyncio.wait_for(future, timeout=4.5))  # Slightly less than 5s hard limit

        # Convert response properly
        response_data = json.loads(response.content) if isinstance(response, JsonResponse) else response
    except SoftTimeLimitExceeded:
        response_data = {"error": "Soft time limit exceeded!"}
    except asyncio.TimeoutError:
        response_data = {"error": "Task forcefully stopped due to timeout!"}
    except Exception as e:
        response_data = {"error": f"Error processing message: {e}"}

    # Send message via WebSocket
    channel_layer = get_channel_layer()
    group_name = f"message_{message_id}"
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "chat.message",
            "message": response_data,
        }
    )

    return response_data