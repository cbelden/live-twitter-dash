import tweepy
from tweepy_oauth import oauth
import redis_store as redis
import json

def trending_terms():
    """Retrieves the trending terms in the USA."""

    # Check cache for trending terms
    terms = json.loads(redis.get('trending-terms'))

    if not terms:
        # Retrieve the top trending terms in the US and store in the cache (4hr expiration)
        api = tweepy.API(oauth)
        usa_woeid = 23424977
        terms = api.trends_place(usa_woeid)[0]['trends']
        redis.setex('trending-terms', json.dumps(terms), 60*60*4)

    return [t['name'] for t in terms]