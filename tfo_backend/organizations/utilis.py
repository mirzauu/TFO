from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from bson import ObjectId
from datetime import datetime

def send_websocket_message(group_id: str, message: dict):
    """
    Send a message to a WebSocket group.
    
    :param group_id: The ID of the WebSocket group.
    :param message: The message dictionary containing data.
    """
    print("Preparing to send WebSocket message...")

    channel_layer = get_channel_layer()
    group_name = f"message_{group_id}"  # WebSocket group name

    print(f"Sending to WebSocket group: {group_name}")

    # Convert ObjectId and datetime to serializable formats
    serialized_message = {
        key: (str(value) if isinstance(value, ObjectId) else 
              value.isoformat() if isinstance(value, datetime) else value)
        for key, value in message.items()
    }

    # Send message to WebSocket group
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "chat.message",
            "message": serialized_message,
        }
    )

    print("WebSocket message sent successfully.")
