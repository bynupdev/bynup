# builder/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import PublishedPage

class EditorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.subdomain = self.scope['url_route']['kwargs']['subdomain']
        self.room_group_name = f'editor_{self.subdomain}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']
        
        if message_type == 'component_update':
            # Broadcast component updates to all clients in the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'component_message',
                    'message': text_data_json
                }
            )
        elif message_type == 'style_update':
            # Broadcast style updates
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'style_message',
                    'message': text_data_json
                }
            )

    # Receive message from room group
    async def component_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'component_update',
            'component_id': message.get('component_id'),
            'action': message.get('action'),
            'html_content': message.get('html_content'),
            'css_content': message.get('css_content')
        }))

    async def style_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'style_update',
            'element_id': message.get('element_id'),
            'styles': message.get('styles')
        }))