# accounts/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .utils import set_user_online, set_user_offline, get_online_users

class PresenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            await self.update_user_status(online=True)
            await self.channel_layer.group_add("presence", self.channel_name)
            await self.accept()
            await self.broadcast_online_users()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.update_user_status(online=False)
            await self.channel_layer.group_discard("presence", self.channel_name)
            await self.broadcast_online_users()

    async def receive(self, text_data):
        if self.user.is_authenticated:
            await self.update_user_status(online=True)
            await self.broadcast_online_users()

    @database_sync_to_async
    def update_user_status(self, online=True):
        if online:
            set_user_online(self.user.id)
        else:
            set_user_offline(self.user.id)

    async def broadcast_online_users(self):
        online_user_ids = await database_sync_to_async(get_online_users)()
        print(f"Broadcasting online users: {online_user_ids}")  # Debug
        await self.channel_layer.group_send(
            "presence",
            {
                "type": "presence_update",
                "online_users": online_user_ids,
            },
        )

    async def presence_update(self, event):
        await self.send(text_data=json.dumps({
            "online_users": event["online_users"]
        }))