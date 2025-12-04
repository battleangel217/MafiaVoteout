import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.core.cache import cache
from channels.db import database_sync_to_async
from django.db.models import F
from google import generativeai as genai
# from django.conf import settings
import os
import markdown
from bs4 import BeautifulSoup
from redis_storage.redis_cache import get_redis_cache, clear_players_cache

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

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
            await update_player_and_rebuild_cache(self.username, self.code, online=False)
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
                player = await get_players(self.username, self.code)
                room = await get_room(self.code)
                print(room)
                if not room:
                    print("hey")
                    await self.send(text_data=json.dumps({
                        "type": "not_found"
                    }))
                    return

                if not room["started"]:
                    await self.send(text_data=json.dumps({
                        "type":"room_started"
                    }))
                    return
                
                if not player:
                    await self.send(text_data=json.dumps({
                        "type": "not_found"
                    }))
                    return
                
                await update_player_and_rebuild_cache(self.username, self.code, online=True)

                
                # send full list
                players = await get_redis_cache(self.code, online_only=True)
                print(players)
                await self.channel_layer.group_send(self.room_group_name, {
                    "type": "player.list",
                    "players": players
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

                if "@idara" in message.lower():
                    try:
                        # Run the AI call in a thread pool to avoid blocking
                        response = await asyncio.to_thread(self._get_ai_response, self.code)
                        
                        # Send AI response to all users in the chat group
                        await self.channel_layer.group_send(self.chat_group_name, {
                            "type": "chat.message",
                            "username": "Idaraobong(AI Bot)",
                            "message": response,
                        })
                    except Exception as e:
                        print(f"AI response error: {e}")
                        await self.send(text_data=json.dumps({
                            "type": "chat_message",
                            "username": "Idaraobong(AI Bot)",
                            "message": "Sorry, I encountered an error while processing your request.",
                        }))
            
                
            elif action == "start_timer":
                duration = data.get("duration", 120)  # default 70 seconds
                # spawn the timer as a background task so we don't block receive()
                await self.start_voting_timer(duration)
                
            elif action == "vote":
                voter = self.username
                votee = data.get("votee")
                await increment_vote(votee, self.code)
                await self.channel_layer.group_send(self.room_group_name, {
                    "type": "vote.recorded",
                    "voter": voter,
                    "votee": votee
                })

            elif action == "kill":
                killed = data.get("votee")
                await delete_user(killed, self.code)
                await self.channel_layer.group_send(self.room_group_name, {
                    "type": "killed",
                    "username": killed
                })
                
            elif action == "game_over":
                await delete_room(code=self.code)
                
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
        message = event["message"]
        username = event["username"]
        message_format = f"{username}: {message}"
        
        # Fire and forget - don't block on message storage
        asyncio.create_task(sync_to_async(store_message)(self.code, message_format))
        
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "username": username,
            "message": message,
        }))

        
    def _get_ai_response(self, code):
        """Synchronous helper to get AI response"""
        from django.db import connection
        
        # Ensure we have a fresh database connection in this thread
        connection.close()
        
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            # Get messages synchronously in this thread
            from Rooms.models import RoomModel as Room
            room = Room.objects.filter(code=code).first()
            
            if not room:
                return "Sorry, I couldn't find the room messages."
            
            messages = room.get_messages()
            
            chat = model.start_chat(history=messages)
            prompt = """
            There is a mafia among these group of people. From all these messages 
            who do you think is the mafia (check for people acting suspicious)? 
            You must give me a person's name and a reason in the format: 
            'I think the mafia is [person's name], because [your reason]'
            Your answer must be very short and brief and precised
            """
            response = chat.send_message(prompt)
            html = markdown.markdown(response.text)

            ai_res = BeautifulSoup(html, "html.parser")
            
            return ai_res
        except Exception as e:
            print(f"Error in _get_ai_response: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

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

    async def killed(self, event):
        await self.send(text_data=json.dumps({
            "type": "killed",
            "killed": event["username"]
        }))

    async def start_voting_timer(self, duration):
        """Start a synchronized voting timer for the room"""
        # Check if there's already an active timer for this room
        existing = self.room_timers.get(self.code)
        if existing:
            task = existing.get('task')
            # If timer is still running, don't start a new one
            if task and not task.done():
                await self.send(text_data=json.dumps({
                    "type": "timer_already_running",
                    "message": "A timer is already running for this room"
                }))
                return
        
        # announce start (non-blocking)
        await self.channel_layer.group_send(self.room_group_name, {
            "type": "start.voting"
        })

        # create and store a background task that runs the countdown
        loop = asyncio.get_running_loop()
        task = loop.create_task(self._run_voting_timer(self.code, duration, self.channel_layer))
        self.room_timers[self.code] = {'task': task, 'owner': self.channel_name, 'duration': duration}

    async def timer_finished(self, event):
        """Handle timer completion"""
        print("helloooo word")
        players = await get_redis_cache(self.code, online_only=True)
        await self.channel_layer.group_send(self.room_group_name, {
            "type": "player.list",
            "players": players
        })
        await delete_user(event["username"], self.code)

        check = await check_mafia(code=self.code)

        if not check:  # Mafia was eliminated
            await self.send(text_data=json.dumps({
                "type": "timer_finished",
                "message": f"You eliminated the mafia. {event['username']} was the mafia",
                "username": event["username"],
                "end": True
            }))
        elif len(players) < 3:
            await self.send(text_data=json.dumps({
                "type": "timer_finished",
                "message": f"You did not eliminate the mafia. {event['username']} was not the mafia",
                "username": event["username"],
                "end": True
            }))
        else:  # Mafia still exists, game continues
            await self.send(text_data=json.dumps({
                "type": "timer_finished",
                "message": f"You did not eliminate the mafia. {event['username']} was not the mafia",
                "username": event["username"]
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

            print("hiiii")

            # finished normally
            self.eliminated_user = await get_highest_vote(self.code)
            print(self.eliminated_user)
            print("debugg")
            await self.channel_layer.group_send(room_group, {
                "type": "timer.finished",
                "username": self.eliminated_user
            })


        except asyncio.CancelledError:
            print("Task endeddd")
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
        await reset_vote(code=self.code)
        await self.send(text_data=json.dumps({
            "type": "start_voting"
        }))
        
    async def not_found(self, event):
        print("Yoji")
        await self.send(text_data=json.dumps({
            "type": "not_found"
        }))


@database_sync_to_async
def get_players(name, code):
    from Players.models import PlayerModel as Player
    return Player.objects.filter(username=name, room=code).values().first()

@database_sync_to_async
def get_room(code):
    from Rooms.models import RoomModel as Room
    return Room.objects.filter(code=code).values().first()


@database_sync_to_async
def increment_vote(votee, code):
    from Players.models import PlayerModel as Player

    p = Player.objects.filter(
        username=votee,
        room=code
    ).update(vote=F('vote') + 1)

    # Rebuild cache for online players
    online_players = list(Player.objects.filter(room=code, online=True))
    online_player_dicts = [p.as_dict() for p in online_players]
    cache.set(f'room_players_{code}:online', online_player_dicts, timeout=60)
    
    # Rebuild cache for all players
    all_players = list(Player.objects.filter(room=code))
    all_player_dicts = [p.as_dict() for p in all_players]
    cache.set(f'room_players_{code}', all_player_dicts, timeout=60)

    return p

@database_sync_to_async
def reset_vote(code):
    from Players.models import PlayerModel as Player
    return Player.objects.filter(
        room=code
    ).update(vote=0)

@database_sync_to_async
def get_highest_vote(code):
    from Players.models import PlayerModel as Player
    p = Player.objects.filter(room=code).order_by("-vote")
    
    if p.count() > 1:
        # Check if there's a tie (multiple players with same highest vote)
        highest_vote = p.first().vote
        if p.filter(vote=highest_vote).count() > 1:
            return "None"
    
    if p.exists():
        return p.first().username
    
    return "None"

@database_sync_to_async
def delete_user(username, code):
    from Players.models import PlayerModel as Player
    Player.objects.filter(username=username).delete()

    # Rebuild cache for online players
    online_players = list(Player.objects.filter(room=code, online=True))
    online_player_dicts = [p.as_dict() for p in online_players]
    cache.set(f'room_players_{code}:online', online_player_dicts, timeout=60)
    
    # Rebuild cache for all players
    all_players = list(Player.objects.filter(room=code))
    all_player_dicts = [p.as_dict() for p in all_players]
    cache.set(f'room_players_{code}', all_player_dicts, timeout=60)

    return

@database_sync_to_async
def check_mafia(code):
    from Players.models import PlayerModel as Player
    return Player.objects.filter(room=code, is_mafia=True).exists()

@database_sync_to_async
def delete_room(code):
    from Rooms.models import RoomModel as Room
    Room.objects.filter(code=code).delete()
    return

@database_sync_to_async
def store_message(code, message):
    from vote.models import MessageModel as Message
    Message.objects.create(room_id=code, message=message)
    return


@database_sync_to_async
def update_player_and_rebuild_cache(username, code, online=False):
    from Players.models import PlayerModel as Player
    
    # Update database
    Player.objects.filter(username=username, room=code).update(online=online)
    
    # Rebuild cache for online players
    online_players = list(Player.objects.filter(room=code, online=True))
    online_player_dicts = [p.as_dict() for p in online_players]
    cache.set(f'room_players_{code}:online', online_player_dicts, timeout=60)
    
    # Rebuild cache for all players
    all_players = list(Player.objects.filter(room=code))
    all_player_dicts = [p.as_dict() for p in all_players]
    cache.set(f'room_players_{code}', all_player_dicts, timeout=60)
