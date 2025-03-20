from rest_framework import serializers
from .models import Organization, OrganizationSubscription,AgentChatSession, ChatMessage, AIAgent,LinkedInAPIKey, SMTPConfiguration, EODReportConfiguration,OrganizationStaff
from organizations.models import Package

class PackageSerializer(serializers.ModelSerializer):
    """
    Serializer for Package details.
    """
    class Meta:
        model = Package
        fields = ['id', 'name', 'description', 'price', 'max_ai_teams', 'max_ivas', 'max_agents', 'features']

class OrganizationStaffSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = OrganizationStaff
        fields = ["id", "username", "email",]

class OrganizationDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for Organization details, including the package details.
    """
    package = PackageSerializer(source='subscription.package')
    user_details = OrganizationStaffSerializer(source="staff",many=True, read_only=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'package', 'user_details']




class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for ChatMessage to retrieve content from MongoDB.
    """
    message = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ['id', 'created_at', 'message']

    def get_message(self, obj):
        message = obj.get_message_from_mongo()
        print(f"MongoDB message for {obj.id}: {message}")  # Debugging line
        return message if message is not None else ""


class ChatMessageIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id','created_at']  # Only fetch the message ID

class AgentChatSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for AgentChatSession with messages.
    """
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = AgentChatSession
        fields = ['id', 'started_at', 'messages']


class CreateChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for creating ChatMessage objects.
    """
    message = serializers.CharField(write_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'created_at', 'message']

    def create(self, validated_data):
        """
        Create a ChatMessage and save its content to MongoDB.
        """
        session = self.context['session']
        message_content = validated_data.pop('message')

        # Create the ChatMessage object
        chat_message = ChatMessage.objects.create(session=session, **validated_data)

        # Save the message content to MongoDB
        chat_message.save_message_to_mongo(message_content)

        return chat_message        


class LinkedInAPIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkedInAPIKey
        fields = ['id', 'access_token', 'created_at', 'updated_at']

class SMTPConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMTPConfiguration
        fields = ['id', 'smtp_host', 'smtp_port', 'password', 'sender_email', 'created_at', 'updated_at']

class EODReportConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EODReportConfiguration
        fields = ['id', 'email_address', 'enable', 'created_at', 'updated_at']    