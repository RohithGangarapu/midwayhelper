import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from app.models import User # Update with your actual Ride model path

class RideTrackingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.ride_id = self.scope['url_route']['kwargs']['ride_id']
        self.room_name = f"track_{self.ride_id}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        # ✅ Step 1: Update DB with latest location
        await self.update_ride_location(self.ride_id, data['lat'], data['lng'])

        # ✅ Step 2: Broadcast to group for live map updates
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'send_location',
                'lat': data['lat'],
                'lng': data['lng'],
            }
        )

    @sync_to_async
    def update_ride_location(self, ride_id, lat, lng):
        try:
            ride = User.objects.get(group=ride_id)
            ride.last_lat = lat
            ride.last_lng = lng
            ride.save()
        except User.DoesNotExist:
            print(f"❌ Ride with ID {ride_id} does not exist.")

    async def send_location(self, event):
        await self.send(text_data=json.dumps({
            'lat': event['lat'],
            'lng': event['lng']
        }))
