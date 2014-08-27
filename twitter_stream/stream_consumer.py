import gevent
import redis_store as redis
import json
import logging


class StreamConsumer(gevent.Greenlet):
    """Consumes items from a redis pubsub channel."""

    def __init__(self, channel, emit):
        """Subscribes to the specified pubsub channel."""

        # Subscribe to the specified channel
        r = redis.Redis()
        self._pubsub = r.pubsub()
        self._pubsub.subscribe(channel)

        # Store the emit function (used to pass data to a socket.io client)
        self._emit = emit

        # Store channel
        self.channel = channel

        # Call Greenlet constructor
        super(StreamConsumer, self).__init__();
        logging.debug("Creating a Consumer: Channel: " + self.channel)

    def _run(self):
        """Listens to the pubsub channel and emits data."""

        for item in self._pubsub.listen():
            if not type(item['data']) is str:
                continue

            logging.debug("Consuming a tweet: Channel: " + self.channel)
            self._emit('twitter-data', {'data': json.loads(item['data'])})

    def kill(self):
        logging.debug("Killing a Consumer. Channel: " + self.channel)
        super(StreamConsumer, self).kill()
