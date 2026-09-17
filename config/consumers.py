import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from main.models import Room, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_slug = self.scope['url_route']['kwargs']['room_slug']
        self.room_group_name = f"chat_{self.room_slug}"

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
        action = data.get('action', 'send')
        user = self.scope['user']

        if not user.is_authenticated:
            return

        if action == 'send':
            message_text = data.get('message', '').strip()
            if message_text:
                msg = await self.save_message(user, self.room_slug, message_text)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'id': msg.id,
                        'message': msg.content,
                        'username': user.username,
                        'created_at': msg.created_at.strftime('%H:%M'),
                    }
                )

        elif action == 'edit':
            msg_id = data.get('id')
            new_content = data.get('content', '').strip()
            if msg_id and new_content:
                success = await self.edit_message(user, msg_id, new_content)
                if success:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'message_edited',
                            'id': msg_id,
                            'content': new_content,
                        }
                    )

        elif action == 'delete':
            msg_id = data.get('id')
            if msg_id:
                success = await self.delete_message(user, msg_id)
                if success:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'message_deleted',
                            'id': msg_id,
                        }
                    )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'action': 'send',
            'id': event['id'],
            'message': event['message'],
            'username': event['username'],
            'created_at': event['created_at'],
        }))

    async def message_edited(self, event):
        await self.send(text_data=json.dumps({
            'action': 'edit',
            'id': event['id'],
            'content': event['content'],
        }))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({
            'action': 'delete',
            'id': event['id'],
        }))

    @database_sync_to_async
    def save_message(self, user, room_slug, content):
        room = Room.objects.get(slug=room_slug)
        return Message.objects.create(user=user, room=room, content=content)

    @database_sync_to_async
    def edit_message(self, user, msg_id, content):
        try:
            msg = Message.objects.get(id=msg_id, user=user)
            msg.content = content
            msg.save()
            return True
        except Message.DoesNotExist:
            return False

    @database_sync_to_async
    def delete_message(self, user, msg_id):
        try:
            msg = Message.objects.get(id=msg_id, user=user)
            msg.delete()
            return True
        except Message.DoesNotExist:
            return False
