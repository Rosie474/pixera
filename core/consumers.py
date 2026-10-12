from email.mime import message
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from core.models import Message, Conversation
from django.contrib.auth.models import User
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"chat_{self.room_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        msg_type = data.get("type", "message")

        if msg_type == "typing":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_event",
                    "sender": data.get("sender"),
                }
            )
            return

        # normal message
        message = data.get("message", "")
        sender = data.get("sender")
        msg_type = data.get("type", "message")

        if not message:
            return
        
        conversation = await self.get_conversation(self.room_id)
        await self.create_message(conversation, sender, message)

        receiver_id = await self.get_other_user(
            conversation,
            sender
        )

        await self.channel_layer.group_send(
            f"user_{receiver_id}",
            {
                "type": "unread_message",
                "conversation_id": conversation.id,
            }
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": sender,
                "conversation_id": self.room_id,
            }
        )

    async def typing_event(self, event):
        await self.send(text_data=json.dumps({
            "typing": True,
            "sender": event["sender"]
    }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "conversation_id": event["conversation_id"],
            # "time": message.created_at.strftime("%H:%M") 
        }))

    @database_sync_to_async
    def get_conversation(self, room_id):
        return Conversation.objects.get(id=room_id)

    @database_sync_to_async
    def create_message(self, conversation, sender, message):
        return Message.objects.create(
            conversation=conversation,
            sender_id=sender,
            text=message,
            is_read=False
        )
    
        conversation.last_message_time = message.created_at,
        conversation.save()
    
    @database_sync_to_async
    def get_other_user(self, conversation, sender_id):
        return conversation.users.exclude(
            id=sender_id
        ).first().id
        


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        self.group_name = f"user_{self.user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def unread_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "unread_message",
            "conversation_id": event["conversation_id"]
        }))