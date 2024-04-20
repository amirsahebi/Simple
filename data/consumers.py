import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer


class Proccess(AsyncWebsocketConsumer):
        async def connect(self):
            self.group_name = "dashboard1"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
    
        async def disconnect(self):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            raise StopConsumer()
    
        
    
        async def send_count1(self, event):
            send_json = json.dumps({"percent": event["percent"],"is_open":event["is_open"],"created_at":event["created_at"],"count":event["count"],"id":event["id"],"starting_node":event["starting_node"],"isgood":event["is_good"],"description":event["description"]})
            await self.send(text_data=send_json)