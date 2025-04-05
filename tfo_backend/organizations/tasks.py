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
from celery import shared_task
from django.core.mail import send_mail
from .models import EODReport, EODReportConfiguration
from django.utils.timezone import now
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


@shared_task(bind=True)
def process_retry_task(self, message_id):
    cache.clear()
    connection.close()  # Ensure fresh DB connection

    count = EmployeeDocuments.objects.count()
    print(f"🔄 Updated EmployeeDocuments count: {count}")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Ensure Celery timeout works (5 min = 300s)
        future = loop.create_task(send_retry_to_view(message_id))
        response = loop.run_until_complete(asyncio.wait_for(future, timeout=299))  # Slightly less than 5 min

        response_data = json.loads(response.content) if isinstance(response, JsonResponse) else response
    except SoftTimeLimitExceeded:
        response_data = {"error": "Soft time limit exceeded!"}
    except asyncio.TimeoutError:
        response_data = {"error": "Task forcefully stopped due to timeout!"}
    except Exception as e:
        response_data = {"error": f"Error processing form: {e}"}

    return response_data


@shared_task(bind=True)
def process_form_task(self, message_id, form_data):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Ensure Celery timeout works (5 min = 300s)
        future = loop.create_task(send_form_to_view(message_id, form_data))
        response = loop.run_until_complete(asyncio.wait_for(future, timeout=299))  # Slightly less than 5 min

        response_data = json.loads(response.content) if isinstance(response, JsonResponse) else response
    except SoftTimeLimitExceeded:
        response_data = {"error": "Task timed out! The process took too long."}
    except asyncio.TimeoutError:
        response_data = {"error": "Task forcefully stopped due to timeout!"}
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
        response = loop.run_until_complete(asyncio.wait_for(future, timeout=299))  # Slightly less than 5s hard limit

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


@shared_task
def send_eod_report():
    """
    Task to send the EOD report emails to organizations that have enabled it.
    """
    today = now().date()

    # SMTP Config
    smtp_host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("EMAIL_PORT", 587))
    sender_email = os.getenv("EMAIL_HOST_USER")
    password = os.getenv("EMAIL_HOST_PASSWORD")

    if not smtp_host or not smtp_port or not sender_email or not password:
        return "❌ Incomplete SMTP configuration."

    for config in EODReportConfiguration.objects.filter(enable=True):
        if config.email_address:
            eod_report = EODReport.objects.filter(organization=config.organization, date=today).first()

            if eod_report:
                agent_usage_details = "\n".join(
                    [f"  - {key}: {value}" for key, value in eod_report.agent_usage.items()]
                ) or "  - No data"

                subject = f"EOD Report for {config.organization.name} - {today}"
                content = f"""
End of Day Report for {config.organization.name} ({today})

Total Logins: {eod_report.total_logins}
Total Chat Sessions: {eod_report.total_chat_sessions}
Total Messages: {eod_report.total_messages}
Total AI Agents Used: {eod_report.total_agents_used}

Agent Usage Details:
{agent_usage_details}
"""

                try:
                    msg = MIMEMultipart()
                    msg["From"] = sender_email
                    msg["To"] = config.email_address
                    msg["Subject"] = subject
                    msg.attach(MIMEText(content, "plain"))

                    with smtplib.SMTP(smtp_host, smtp_port) as server:
                        server.starttls()
                        server.login(sender_email, password)
                        server.send_message(msg)

                except Exception as e:
                    print(f"❌ Failed to send report to {config.email_address}: {e}")

    return "✅ EOD Reports Task Completed"