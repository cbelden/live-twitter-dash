"""Wrapper class to access the appropriate redis instance depending on the environment."""
import redis
import os


def Redis():
    _redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    return redis.from_url(_redis_url)

def pubsub():
    return Redis().pubsub();