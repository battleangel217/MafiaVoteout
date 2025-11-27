import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.core.cache import cache
from channels.db import database_sync_to_async
from django.db.models import F

class VotingConsumer(AsyncWebsocketConsumer):
    # Class-level dict to track timers per room
    # room_timers maps room_code -> dict with keys:
    #   'task' -> asyncio.Task running the timer
    #   'owner' -> channel_name of the consumer that started it
    #   'duration' -> requested duration
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
                print(self.code)
                # mark player online
                player = await self.get_players(self.username, self.code)
                room = await self.get_room(self.code)
                if not room:
                    await self.channel_layer.group_send(self.room_group_name, {
                        "type": "not.found"
                    })
                    return

                if not room["started"]:
                    await self.send(text_data=json.dumps({
                        "type":"room_started"
                    }))
                    return
                await sync_to_async(Player.objects.filter(username=self.username, room=self.code).update)(online=True)

                if not player:
                    await self.channel_layer.group_send(self.chat_group_name, {
                        "type": "not.found"
                    })
                    return

                
                # send full list
                players = await sync_to_async(list)(Player.objects.filter(room=self.code, online=True))
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
                duration = data.get("duration", 70)  # default 70 seconds
                # spawn the timer as a background task so we don't block receive()
                await self.start_voting_timer(duration)
                
            elif action == "vote":
                voter = self.username
                votee = data.get("votee")
                await sync_to_async(Player.objects.filter(username=votee, room=self.code).update)(vote=F('vote') + 1)
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
            "type": "vote_recorded",
            "voter": event.get("voter"),
            "votee": event.get("votee")
        }))

    async def start_voting_timer(self, duration):
        """Start a synchronized voting timer for the room"""
        timer_key = f"timer_{self.code}"
        # If there is an existing timer for the room started by someone else, cancel it
        existing = self.room_timers.get(self.code)
        if existing:
            task = existing.get('task')
            # cancel previous task
            if task and not task.done():
                task.cancel()

        # announce start (non-blocking)
        await self.channel_layer.group_send(self.room_group_name, {
            "type": "start.voting"
        })

        # create and store a background task that runs the countdown
        # store the owner so we can cancel it on disconnect from that connection
        loop = asyncio.get_running_loop()
        task = loop.create_task(self._run_voting_timer(self.code, duration, self.channel_layer))
        self.room_timers[self.code] = {'task': task, 'owner': self.channel_name, 'duration': duration}

    async def timer_finished(self, event):
        """Handle timer completion"""
        from Players.models import PlayerModel as Player
        players = await sync_to_async(list)(Player.objects.filter(room=self.code, online=True))
        await self.channel_layer.group_send(self.room_group_name, {
            "type": "player.list",
            "players": [p.as_dict() for p in players]
        })
        await self.send(text_data=json.dumps({
            "type": "timer_finished"
        }))

    async def _run_voting_timer(self, code, duration, channel_layer):
        """Background task that sends timer ticks and finishes.

        This function is run as an independent asyncio.Task so it can be cancelled
        without blocking the consumer instance shutdown.
        """
        timer_group = f"timer_{code}"
        room_group = f"room_{code}"
        try:
            for seconds_left in range(duration, -1, -1):
                # If the task is cancelled, this will raise CancelledError and jump to except
                await channel_layer.group_send(timer_group, {
                    "type": "timer",
                    "time_left": seconds_left,
                    "total_duration": duration
                })
                await asyncio.sleep(1)

            # finished normally
            await channel_layer.group_send(room_group, {"type": "timer.finished"})

        except asyncio.CancelledError:
            # Clean up on cancellation: notify room that timer was stopped if desired
            # (optional) we can send a final message; for now we quietly exit.
            return
        finally:
            # remove from room_timers if still present
            existing = self.room_timers.get(code)
            if existing and existing.get('task') is asyncio.current_task():
                try:
                    del self.room_timers[code]
                except KeyError:
                    pass

    async def start_voting(self, event):
        await self.send(text_data=json.dumps({
            "type": "start_voting"
        }))
        
    async def not_found(self, event):
        await self.send(text_data=json.dumps({
            "type": "not_found"
        }))

    @database_sync_to_async
    def get_players(self, name, code):
        from Players.models import PlayerModel as Player
        return Player.objects.filter(username=name, room=code).values().first()
    
    @database_sync_to_async
    def get_room(self, code):
        from Rooms.models import RoomModel as Room
        return Room.objects.filter(code=code).values().first()