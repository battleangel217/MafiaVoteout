# ...existing code...
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.core.cache import cache
from redis_storage.redis_cache import clear_players_cache, get_redis_cache

class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from Players.models import PlayerModel as Player

        self.code = self.scope['url_route']['kwargs']['code']
        self.lobby_group_name = f"lobby_{self.code}"
        self.chat_group_name = f"chat_{self.code}"
        await self.channel_layer.group_add(self.lobby_group_name, self.channel_name)
        await self.channel_layer.group_add(self.chat_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # mark offline if username was set
        from Players.models import PlayerModel as Player
        self.username = getattr(self, "username", None)
        if self.username:
            print("did this work?")
            await update_player_and_rebuild_cache(self.username, self.code, online=False)
            await self.channel_layer.group_send(self.lobby_group_name, {
                "type": "player.left",
                "player": {"username": self.username}
            })
        await self.channel_layer.group_discard(self.lobby_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            from Players.models import PlayerModel as Player
            data = json.loads(text_data)
            action = data.get("action")
            if action == "join":
                self.username = data.get("username")
                print(self.username)
                await update_player_and_rebuild_cache(self.username, self.code, online=True)
                player = await get_players(self.username, self.code)
                print(player)
                if not player:
                    await self.channel_layer.group_send(self.chat_group_name, {
                        "type": "not.found"
                    })
                    return
                
                # send full list
                players = await get_redis_cache(self.code)
                await self.channel_layer.group_send(self.lobby_group_name, {
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
            elif action == "start_game":
                random_player = await sync_to_async(lambda: Player.objects.filter(room=self.code).order_by('?').first())()

                # Update the field
                if random_player:
                    random_player.is_mafia = True
                    await sync_to_async(random_player.save)()
                await self.channel_layer.group_send(self.lobby_group_name, {
                    "type": "start.game",
                })
            elif action == "heartbeat":
                # optional keepalive
                pass
        except json.JSONDecodeError:
            print("Received invalid JSON")
        except Exception as e:
            print(f"Error in receive: {e}")  # Log the error


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


    async def start_game(self, event):
        from Rooms.models import RoomModel as Room
        await sync_to_async(Room.objects.filter(code=self.code).update)(started=True)
        await self.send(text_data=json.dumps({
            "type": "start_game"
        }))

    async def not_found(self, event):
        await self.send(text_data=json.dumps({
            "type": "not_found"
        }))


@database_sync_to_async
def update_player_and_rebuild_cache(username, code, online=False):
    from Players.models import PlayerModel as Player
    
    # Update database
    Player.objects.filter(username=username, room=code).update(online=online)
    # Try to update caches incrementally to avoid expensive full rebuilds
    key_all = f'room_players_{code}'
    key_online = f'room_players_{code}:online'

    # Update cached "all players" list if present
    all_players = cache.get(key_all)
    if all_players is not None:
        found = False
        for p in all_players:
            if p.get('username') == username:
                p['online'] = online
                found = True
                break
        if not found and online:
            all_players.append({
                "username": username,
                "isAdmin": False,
                "online": online,
                "isMafia": False,
                "vote": 0,
            })
        cache.set(key_all, all_players, timeout=120)

    # Update cached "online players" list if present
    online_players = cache.get(key_online)
    if online_players is not None:
        if online:
            if not any(p.get('username') == username for p in online_players):
                player_entry = None
                if all_players is not None:
                    for p in all_players:
                        if p.get('username') == username:
                            player_entry = p
                            break
                if player_entry is None:
                    player_entry = {
                        "username": username,
                        "isAdmin": False,
                        "online": online,
                        "isMafia": False,
                        "vote": 0,
                    }
                online_players.append(player_entry)
        else:
            online_players = [p for p in online_players if p.get('username') != username]

        cache.set(key_online, online_players, timeout=120)

    # If no cache existed at all, clear keys so next read will rebuild from DB
    if all_players is None and online_players is None:
        cache.delete(key_all)
        cache.delete(key_online)

@database_sync_to_async
def get_players(name, code):
    from Players.models import PlayerModel as Player
    return Player.objects.filter(username=name, room=code).values().first()