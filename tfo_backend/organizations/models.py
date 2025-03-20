from django.db import models
import uuid
from django.contrib.postgres.fields import JSONField
from pymongo import MongoClient
from datetime import datetime
from datetime import datetime
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from bson.objectid import ObjectId
from pymongo import DESCENDING
from pymongo import ReturnDocument
from django.utils.timezone import now

from django.db.models.signals import post_save
from django.dispatch import receiver
# MongoDB setup
from tfo_backend.mongodb import chat_collection,db

class Organization(models.Model):
    """
    Organization model representing a client entity under a company.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class LinkedInAPIKey(models.Model):
    """
    Model for storing LinkedIn API keys associated with an organization.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='linkedin_api_keys')
    access_token = models.TextField(blank=True, null=True, help_text="OAuth Access Token")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.organization} - LinkedIn API"
    
class SMTPConfiguration(models.Model):
    """
    Model for storing SMTP email configurations for an organization.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='smtp_configs')
    smtp_host = models.CharField(max_length=255, help_text="SMTP server host address", blank=True, null=True)
    smtp_port = models.PositiveIntegerField(help_text="SMTP server port", blank=True, null=True)
    password = models.CharField(max_length=255, help_text="SMTP password (should be stored securely)", blank=True, null=True)
    sender_email = models.EmailField(help_text="Email address used as sender", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.organization} - {self.sender_email}"    

class EODReportConfiguration(models.Model):
    """
    Model for configuring End of Day (EOD) report settings for an organization.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='eod_report_configs')
    email_address = models.EmailField(help_text="Email address to receive EOD reports", blank=True, null=True)
    enable = models.BooleanField(default=False, help_text="Enable or disable EOD report emails")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.organization} - EOD Report ({'Enabled' if self.enable else 'Disabled'})"

@receiver(post_save, sender=Organization)
def create_default_configs(sender, instance, created, **kwargs):
    if created:
        LinkedInAPIKey.objects.create(organization=instance)
        SMTPConfiguration.objects.create(organization=instance)
        EODReportConfiguration.objects.create(organization=instance)


class OrganizationStaff(models.Model):
    """
    OrganizationStaff model representing employees of an organization.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)  # Links to the User model
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='staff')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.organization.name


class Package(models.Model):
    """
    Represents a subscription package available to organizations.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)  # Package name, e.g., "Basic", "Premium"
    description = models.TextField(blank=True, null=True)  # Optional description of the package
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Package price
    max_ai_teams = models.PositiveIntegerField(default=1)  # Max number of AI teams
    max_ivas = models.PositiveIntegerField(default=2)  # Max number of IVAs
    max_agents = models.PositiveIntegerField(default=5)  # Max number of agents
    features = models.JSONField(default=dict)  # JSON field to store additional features
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class OrganizationSubscription(models.Model):
    """
    Tracks an organization's subscription to a specific package.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.OneToOneField(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    package = models.ForeignKey(Package, on_delete=models.PROTECT, related_name='subscriptions')
    start_date = models.DateField(auto_now_add=True)  # Subscription start date
    end_date = models.DateField(null=True, blank=True)  # Optional subscription expiry date
    active = models.BooleanField(default=True)  # Is the subscription currently active

    def __str__(self):
        return f"{self.organization.name} - {self.package.name}"
    
 

class AIAgent(models.Model):
    """Represents an AI Agent."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name




class AgentChatSession(models.Model):
    """
    Represents a session between a user and an AI agent.
    - Each session belongs to one user.
    - Each session is associated with one AI agent.
    """
    id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='organization_chat_session'
    )
    agent = models.ForeignKey(AIAgent, on_delete=models.CASCADE, related_name="chat_sessions")
    started_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" {self.organization} --------{self.agent.name}"


class ChatMessage(models.Model):
    """
    Represents metadata for a chat message stored in MongoDB.
    - Each message is linked to an AgentChatSession.
    - Actual message content is stored in MongoDB.
    """
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(AgentChatSession, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name="chat_messages",default="0207608f-9130-4065-b1fd-646bda67516f")
    created_at = models.DateTimeField(auto_now_add=True)

    def get_next_sequence(self,name):
        """
        Get the next auto-incrementing sequence number for a given counter name.
        """
        counter = db.counters.find_one_and_update(
            {"_id": name},
            {"$inc": {"seq": 1}},  # Increment the counter
            upsert=True,  # Create if not exists
            return_document=ReturnDocument.AFTER
        )
        return counter["seq"]
    def message_to_mongo(self, message_data):
        """
        Save the message content to MongoDB with dynamic fields.
        :param message_data: A dictionary containing the message content and any additional data.
        """
        try:
            message_number = self.get_next_sequence("message_number")
            message_document = {
                "chat_message_id": str(self.id),
                "session_id": str(self.session.id),
                "message_number": message_number,
                "timestamp": datetime.now(),
                **message_data,
            }
            chat_collection.insert_one(message_document)
            print("Message saved to MongoDB:", message_document)
        except Exception as e:
            print(f"Error saving message to MongoDB: {e}")



    def save_message_to_mongo(self, message_data, task_name):
        """
        Save or update message content in MongoDB with an auto-incrementing field.
        """
        filter_query = {
            "chat_message_id": str(self.id),  # Unique identifier for task updates
            "task_name": task_name  # Match by task_name
        }
      
        # Get the next sequence number for message_number
        message_number = self.get_next_sequence("message_number")

        # Create a new document or update data
        new_document = {
            "chat_message_id": str(self.id),
            "session_id": str(self.session.id),
            "timestamp": datetime.now().isoformat(),
            "message_number": message_number,  # Auto-increment field
            **message_data  # Include dynamic fields from message_data
        }
        
        
        chat_collection.replace_one(filter_query, new_document, upsert=True)
       
        self.notify_websocket_group(new_document)
            
    def save_task_update_to_mongo(self, message_data):
        """
        Save or update message content in MongoDB.
        """
        filter_query = {"chat_message_id": str(self.id)}  # Unique identifier for updates
        new_document = {
            "chat_message_id": str(self.id),
            "session_id": str(self.session.id),
            "timestamp": datetime.utcnow(),
            **message_data  # Include dynamic fields from message_data
        }

        # Update if exists, otherwise insert and get the document ID
        chat_collection.replace_one(filter_query, new_document, upsert=True)

        # Fetch the updated/inserted document
        updated_document = chat_collection.find_one(filter_query)

        # Construct the response with the required fields
       
        self.notify_websocket_group(new_document)

    def notify_websocket_group(self, message_document):
        """
        Notify WebSocket group with the new message.
        :param message_document: The complete message document from MongoDB.
        """
        print("reached notify")
        channel_layer = get_channel_layer()
        group_name = f"message_{self.id}"
   
        print("reached notify",group_name)
        # Prepare the message to be sent dynamically
        # Convert ObjectId and other non-serializable types
        serialized_message = {
            key: (str(value) if isinstance(value, ObjectId) else 
                value.isoformat() if isinstance(value, datetime) else value)
            for key, value in message_document.items()
        }

        # Send the message to the WebSocket group
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "chat.message",
                "message": serialized_message,  # Send the entire dynamic message
            }
        )


    def get_message_from_mongo(self):
        """
        Retrieve the message content from MongoDB.
        :return: The message content or None if not found.
        """
        from pymongo import ASCENDING

        message_document = chat_collection.find_one(
            {"chat_message_id": str(self.id)},
            sort=[("timestamp", ASCENDING)]  # Sort by timestamp in ascending order
        )
        return message_document if message_document else None
    


class EODReport(models.Model):
    """
    Stores End of Day (EOD) reports for organizations.
    This tracks login stats, chat sessions, messages, and AI agent activity.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='eod_reports')
    date = models.DateField(default=now)  # Tracks EOD data per day
    total_logins = models.PositiveIntegerField(default=0)  # Number of logins today
    total_chat_sessions = models.PositiveIntegerField(default=0)  # AI chat sessions today
    total_messages = models.PositiveIntegerField(default=0)  # Total messages exchanged
    total_agents_used = models.PositiveIntegerField(default=0)  # AI agents active today
    agent_usage = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('organization', 'date')  # Ensure one report per day per org

    def __str__(self):
        return f"EOD Report: {self.organization.name} - {self.date}"


class UserLoginLog(models.Model):
    """
    Logs each user login attempt, storing timestamps, IP, and device details.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name="login_logs")
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name="login_logs")
    timestamp = models.DateTimeField(auto_now_add=True)  # When user logged in
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Store user IP
    user_agent = models.TextField(blank=True, null=True)  # Store browser/device info

    def __str__(self):
        return f"{self.user.username} logged in at {self.timestamp}"