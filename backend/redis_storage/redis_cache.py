from django.core.cache import cache
from channels.db import database_sync_to_async
from Players.models import PlayerModel as Player


@database_sync_to_async
def get_redis_cache(code, online_only=False):
    cache_key = f"room_players_{code}:online" if online_only else f"room_players_{code}"

    cached_players = cache.get(cache_key)
    if cached_players is not None:
        return cached_players
    
    if online_only:
        players = list(Player.objects.filter(room=code, online=True))
    else:
        players = list(Player.objects.filter(room=code))
    
    # Convert to dictionaries for caching
    player_dicts = [p.as_dict() for p in players]
    
    # Store in Redis for 30 seconds
    cache.set(cache_key, player_dicts, timeout=120)
    
    return player_dicts


def clear_players_cache(code):
    """Clear player cache for a room - call this whenever players change"""
    cache.delete(f'room_players_{code}:online')
    cache.delete(f'room_players_{code}')