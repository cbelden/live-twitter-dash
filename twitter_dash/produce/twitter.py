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

        print "Recieved a new tweet."

        # Only get tweets that contain the tracking terms
        for term in self._tracking:
            if term.lower() not in status.text.lower():
                print ">>>Term not found: ", term
                print ">>>", status.text
                return

        # Get user profile photo
        user = status.user
        screen_name = user.screen_name
        img_url = user.profile_image_url

        # Publish the data
        data = {'text': text,
                'user_image_url': img_url,
                'screen_name': screen_name}
        self._redis.publish(self._channel, json.dumps(data))

        # Throttle our results
        time.sleep(1)

class TwitterFeedProducer(gevent.Greenlet):
    """Defines a Greenlet that publishes twitter data to redis."""
    
    def __init__(self, tracking):
        """Creates instance of CustomStreamListener."""

        self._stream_listener = CustomStreamListener(tracking)

        # The name of the channel will be the alpha-sorted tracking terms as a list.
        self.channel = json.dumps(sorted(tracking))
        self.tracking = tracking
        print "Creating a Producer: channel-", self.channel

        # Initialize the client list
        self.clients = []

        # Call gevent.Greenlet constructor
        super(TwitterFeedProducer, self).__init__()

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

        print "Starting filter on: ", self.tracking
        stream.filter(track=self.tracking)

    def add_client(self, user):
        """Increments the number of clients."""
        self.clients.append(user)

    def remove_client(self, user):
        """Decrements the number of clients. Kills self if the count is below 1."""
        self.clients.remove(user)

        if len(self.clients) < 1:
            print "Producer client size is now 0. Killing: channel-", self.channel
            self.kill()

class DebugTwitterFeedProducer(TwitterFeedProducer):

    def _run(self):

        # Get redis instance
        r = redis.Redis()

        # Publish data forever
        while True:
            time.sleep(2)
            r.publish(self.channel, json.dumps({'text': 'This is a tweet.', 'user_image_url': '/static/img/raspberry-pi.png'}))
