from error import StreamErrorMessage
import tweepy
import os
import redis_store as redis
import json
import time
import gevent
import logging


class TwitterStreamListener(tweepy.StreamListener):
    """Listens to a twitter stream and publishes tweets to redis."""

    def __init__(self, tracking):
        """Initializes the stream producer."""

        # Get redis instance
        self._redis = redis.Redis()
        self._tracking = tracking
        self._channel = json.dumps(sorted(tracking))

        # Call tweepy.StreamListener constructor
        super(TwitterStreamListener, self).__init__()

    def on_status(self, status):
        """Publishes the Tweet to redis."""

        # Get text
        text = status.text.encode('utf8')

        # Only get tweets that contain the tracking terms
        for term in self._tracking:
            if term.lower() not in status.text.lower():
                return

        # Extract twitter info
        user = status.user
        img_url = user.profile_image_url
        screen_name = user.screen_name
        str_id = status.id_str
        tweet_url = '/'.join(["https://twitter.com", screen_name, "status", str_id])
        created_at = str(status.created_at)

        data = {'text': text,
                'image_url': img_url,
                'screen_name': screen_name,
                'tweet_url': tweet_url,
                'created_at': created_at}

        # Publish the data
        logging.info('Publishing tweet to channel: ' + self._channel)
        self._redis.publish(self._channel, json.dumps(data))

        # Throttle our results
        time.sleep(1)

class StreamProducer(gevent.Greenlet):
    """Defines a Greenlet that publishes twitter data to redis."""
    
    def __init__(self, tracking, _TwitterListener=None):
        """Initializes the stream producer."""

        # Set up the twitter listener
        if not _TwitterListener:
            _TwitterListener = TwitterStreamListener

        self._stream_listener = _TwitterListener(tracking)

        # Set up the redis pubsub channel
        self.channel = json.dumps(sorted(tracking))
        self.tracking = tracking
        logging.info('Creating a Producer. Channel: ' + self.channel)

        # Call parent constructor
        super(StreamProducer, self).__init__()

    def _run(self):
        """Starts the twitter stream listener/redis-publisher."""

        # Authorize tweepy
        consumer_key = os.environ['TWITTER_CONSUMER_KEY']
        consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
        access_token = os.environ['TWITTER_ACCESS_TOKEN']
        access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
        oauth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        oauth.set_access_token(access_token, access_token_secret)

        # Listen to the stream of tweets containing the words/hashtags in 'filtering'
        stream = tweepy.Stream(oauth, self._stream_listener)

        try:
            stream.filter(track=self.tracking)
        except Exception:
            logging.exception('Error with tweepy.')
            # Emit error message to user
            r = redis.Redis()
            r.publish(self.channel, json.dumps(StreamErrorMessage))

    def kill(self):
        """Logs the producer's information before killing the greenlet."""
        logging.info('Killing Producer. Channel: ' + self.channel)
        super(StreamProducer, self).kill()


class DebugStreamProducer(StreamProducer):
    """Publishes tweets forever."""

    def __init__(self, tracking):
        self.channel = json.dumps(sorted(tracking))
        super(StreamProducer, self).__init__()

    def _run(self):
        """Publish tweets forever."""
        r = redis.Redis()
        while True:
            time.sleep(2)
            data = {'text': 'This is a tweet',
                    'image_url': '/static/img/raspberry-pi.png',
                    'screen_name': 'somecooldude',
                    'tweet_url': '#',
                    'created_at': 'never'}
            r.publish(self.channel, json.dumps(data))
