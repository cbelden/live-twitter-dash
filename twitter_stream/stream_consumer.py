import gevent
import redis
import json


class StreamConsumer(gevent.Greenlet):
    """Consumes items from a redis pubsub channel."""

    def __init__(self, channel, emit):
        """Subscribes to the specified pubsub channel."""

        print "Creating a Consumer: channel-", channel

        # Subscribe to the specified channel
        redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
        self._redis = redis.from_url(redis_url)
        self._pubsub = r.pubsub()
        self._pubsub.subscribe(channel)

        # Store the emit function (used to pass data to a socket.io client)
        self._emit = emit

        # Store channel
        self.channel = channel

        # Call Greenlet constructor
        super(StreamConsumer, self).__init__();

    def _run(self):
        """Listens to the pubsub channel and emits data."""

        for item in self._pubsub.listen():
            if not type(item['data']) is str:
                continue

            print '>>> emitting a tweet.'
            self._emit('twitter-data', {'data': json.loads(item['data'])})

    def kill(self):
        print "Killing a Consumer: channel-", self.channel
        super(StreamConsumer, self).kill()
