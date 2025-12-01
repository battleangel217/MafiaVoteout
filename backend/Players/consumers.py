import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the room name and username from the URL
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.username = self.scope['url_route']['kwargs']['username']
        self.room_group_name = f"chat_{self.room_name}"

        # Join the group for that room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Announce join to others
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_event",
                "message": f"{self.username} joined the chat!"
            }
        )

    async def disconnect(self, close_code):
        # Leave the group when disconnected
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Announce leave event
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_event",
                "message": f"{self.username} left the chat."
            }
        )

    # When a client sends a message
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        # Broadcast it to everyone in the same group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "username": self.username,
                "message": message
            }
        )

    # Called when message is sent to the group
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "username": event["username"],
            "message": event["message"]
        }))

    # Called when a user joins or leaves
    async def user_event(self, event):
        await self.send(text_data=json.dumps({
            "system": True,
            "message": event["message"]
        }))
