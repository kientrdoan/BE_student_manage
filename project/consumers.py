from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json

class MyConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = "enrollment_reload"
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()
        print("WebSocket connected")

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
        print("WebSocket disconnected")

    # Hàm xử lý broadcast từ backend
    def send_reload(self, event):
        self.send(text_data=json.dumps({"message": event["message"]}))
