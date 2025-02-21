# accounts/utils.py
import redis
from django.conf import settings

redis_client = redis.StrictRedis(host="127.0.0.1", port=6379, db=0, decode_responses=True)

def set_user_online(user_id):
    key = f"online_users:{user_id}"
    redis_client.setex(key, 30, "1")
    print(f"Set user {user_id} online")  # Debug

def set_user_offline(user_id):
    key = f"online_users:{user_id}"
    redis_client.delete(key)
    print(f"Set user {user_id} offline")  # Debug

def is_user_online(user_id):
    key = f"online_users:{user_id}"
    return redis_client.exists(key)

def get_online_users():
    keys = redis_client.keys("online_users:*")
    online_ids = [int(key.split(":")[1]) for key in keys]
    print(f"Online user IDs: {online_ids}")  # Debug
    return online_ids