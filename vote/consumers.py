import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.core.cache import cache

class VotingConsumer(AsyncWebsocketConsumer):
    # Class-level dict to track timers per room
    room_timers = {}

    async def connect(self):
        self.code = self.scope['url_route']['kwargs']['code']
        self.room_group_name = f"room_{self.code}"
        self.chat_group_name = f"roomchat_{self.code}"
        self.timer_group_name = f"timer_{self.code}"
        self.username = None
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.channel_layer.group_add(self.chat_group_name, self.channel_name)
        await self.channel_layer.group_add(self.timer_group_name, self.channel_name)
        print('ge')
        await self.accept()


    async def disconnect(self, close_code):
        # mark offline if username was set
        from Players.models import PlayerModel as Player
        self.username = getattr(self, "username", None)
        if self.username:
            await sync_to_async(Player.objects.filter(username=self.username, room=self.code).update)(online=False)
            await self.channel_layer.group_send(self.room_group_name, {
                "type": "player.left",
                "player": {"username": self.username}
            })
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.timer_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            from Players.models import PlayerModel as Player
            data = json.loads(text_data)
            action = data.get("action")
            
            if action == "join":
                self.username = data.get("username")
                print(self.username)
                
                # send full list
                players = await sync_to_async(list)(Player.objects.filter(room=self.code))
                print(players)
                await self.channel_layer.group_send(self.room_group_name, {
                    "type": "player.list",
                    "players": [p.as_dict() for p in players]
                })

                await self.channel_layer.group_send(self.chat_group_name, {
                    "type": "player.join",
                    "username": self.username
                })
                
            elif action == "message":
                message = data.get("message")
                await self.channel_layer.group_send(self.chat_group_name, {
                    "type": "chat.message",
                    "username": self.username,
                    "message": message,
                })
                
            elif action == "start_timer":
                duration = data.get("duration", 70)  # default 120 seconds
                await self.start_voting_timer(duration)
                
            elif action == "vote":
                voter = self.username
                votee = data.get("votee")
                await self.channel_layer.group_send(self.room_group_name, {
                    "type": "vote.recorded",
                    "voter": voter,
                    "votee": votee
                })
                
            elif action == "heartbeat":
                # optional keepalive
                pass
                
        except json.JSONDecodeError:
            print("Received invalid JSON")
        except Exception as e:
            print(f"Error in receive: {e}")


    async def timer(self, event):
        await self.send(text_data=json.dumps({
            "type": "timer",
            "time_left": event["time_left"],
        }))

    async def player_join(self, event):
        await self.send(text_data=json.dumps(
            {
                "type": "player_join",
                "username": event["username"]
            }
        )
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "username": event["username"],
            "message": event["message"],
        }))

    # group message handlers:
    async def player_list(self, event):
        await self.send(text_data=json.dumps({
            "type": "player_list",
            "players": event["players"],
        }))

    async def player_left(self, event):
        await self.send(text_data=json.dumps({
            "type": "player_left",
            "player": event["player"],
        }))

    async def vote_recorded(self, event):
        await self.send(text_data=json.dumps({
            "type": "vote.recorded",
            "voter": event.get("voter"),
            "votee": event.get("votee")
        }))

    async def start_voting_timer(self, duration):
        """Start a synchronized voting timer for the room"""
        timer_key = f"timer_{self.code}"
        
        # Stop existing timer if running
        if self.code in self.room_timers:
            self.room_timers[self.code]['stop'] = True

        await self.channel_layer.group_send(self.room_group_name, {
            "type": "start.voting"
        })
        
        # Mark timer as running
        timer_data = {'stop': False, 'duration': duration}
        self.room_timers[self.code] = timer_data
        
        # Run timer countdown
        for seconds_left in range(duration, -1, -1):
            if timer_data['stop']:
                break
                
            await self.channel_layer.group_send(self.timer_group_name, {
                "type": "timer",
                "time_left": seconds_left,
                "total_duration": duration
            })
            
            # Wait 1 second before next tick
            await asyncio.sleep(1)
        
        # Timer finished - notify room
        await self.channel_layer.group_send(self.room_group_name, {
            "type": "timer.finished",
        })
        
        # Clean up
        if self.code in self.room_timers:
            del self.room_timers[self.code]

    async def timer_finished(self, event):
        """Handle timer completion"""
        await self.send(text_data=json.dumps({
            "type": "timer_finished"
        }))

    async def start_voting(self, event):
        await self.send(text_data=json.dumps({
            "type": "start_voting"
        }))
        