import tweepy
import os
import redis
import json
import time
import gevent


class CustomStreamListener(tweepy.StreamListener):
    """Listens to a twitter stream and publishes tweets to redis."""

    def __init__(self, tracking):
        """Gets redis instance."""

        self._redis = redis.Redis()
        self._tracking = tracking
        self._channel = json.dumps(sorted(tracking))

        # Call StreamListener constructor
        super(CustomStreamListener, self).__init__()

    def on_status(self, status):
        """Publishes the Tweet to redis."""

        # Get text
        text = status.text.encode('utf8')

        # Only get tweets that contain the tracking terms
        for term in self._tracking:
            if term.lower() not in status.text.lower():
                return

        # Get user profile photo
        user = status.user
        screen_name = user.screen_name
        img_url = user.profile_image_url
        str_id = status.id_str
        tweet_url = '/'.join(["https://twitter.com", screen_name, "status", str_id])

        # Publish the data
        data = {'text': text,
                'user_image_url': img_url,
                'screen_name': screen_name,
                'tweet_url': tweet_url}
        self._redis.publish(self._channel, json.dumps(data))

        # Throttle our results
        time.sleep(1)

class StreamProducer(gevent.Greenlet):
    """Defines a Greenlet that publishes twitter data to redis."""
    
    def __init__(self, tracking):
        """Creates instance of CustomStreamListener."""

        self._stream_listener = CustomStreamListener(tracking)

        # The name of the channel will be the alpha-sorted tracking terms as a list.
        self.channel = json.dumps(sorted(tracking))
        self.tracking = tracking
        print "Creating a Producer: channel-", self.channel

        # Call gevent.Greenlet constructor
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
        except Exception, e:
            print e
            # Emit error message to user
            r = redis.Redis()
            msg = {"text": "Sorry! Encountered an error while streaming tweets. Please start a new Stream.",
                   "user_image_url": "static/img/error.png",
                   "screen_name": "TwitterDash",
                   "tweet_url": ""}
            r.publish(self.channel, json.dumps(msg))


class DebugStreamProducer(StreamProducer):

    def _run(self):

        # Get redis instance
        r = redis.Redis()

        # Publish data forever
        while True:
            time.sleep(2)
            r.publish(self.channel, json.dumps({'text': 'This is a tweet.', 'user_image_url': '/static/img/raspberry-pi.png'}))
