from stream_consumer import StreamConsumer
from stream_producer import StreamProducer
import json


class StreamServer():
    """Manages the stream producers/clients."""

    def __init__(self, producer_class=None, consumer_class=None):
        """Initializes the StreamManager object."""

        self._producers = {}        # Pool of producers
        self._consumers = {}        # Each socketio session's consumer
        self._terms = {}            # Stores the filtering terms of each client

        # Set up the default producer class
        if not producer_class:
            producer_class = StreamProducer

        # Set up the default consumer class
        if not consumer_class:
            consumer_class = StreamConsumer

        self._ProducerClass = producer_class
        self._ConsumerClass = consumer_class


    def spawn_stream(self, socketio_conn):
        """Creates and starts a Twitter stream producer and consumer."""
        
        self.spawn_consumer(socketio_conn)
        self.spawn_producer(socketio_conn)


    def spawn_consumer(self, socketio_conn):
        """Creates a new stream consumer."""

        # Get connection info
        tracking_terms = socketio_conn.tracking_terms
        emit = socketio_conn.emit
        sessid = socketio_conn.sessid

        # Create the stream consumer
        channel = json.dumps(sorted(tracking_terms))
        stream_consumer = self._ConsumerClass(channel, emit)

        # Kill old consumer
        if sessid in self._consumers:
            self._consumers[sessid].kill()

        # Start the greenlet and store in _consumers
        stream_consumer.start()
        self._consumers[sessid] = stream_consumer

    def spawn_producer(self, socketio_conn):
        """Spawns a new stream producer."""
        # Get connection info
        sessid = socketio_conn.sessid
        tracking_terms = socketio_conn.tracking_terms
        terms = frozenset(tracking_terms)

        # Create and start a new producer if it doesn't exist
        if terms not in self._producers:
            feed_producer = self._ProducerClass(tracking_terms)
            feed_producer.start()
            self._producers[terms] = feed_producer

        # Add/Update record of this client
        self._terms[sessid] = terms

        # Kill any producers who may have lost its last client
        self._clean_producers()

    def kill_connection(self, socketio_conn):
        """
        Kills the stream consumer specified by the userid and tracking terms, removes
        the connection from the dict of clients, and kills the stream producer if this
        is its last client.
        """

        # Remove the sessid record from the terms dict
        sessid = socketio_conn.sessid
        if sessid in self._terms:
            del self._terms[sessid]

        # Kill/Delete the consumer
        consumer = self._consumers.get(sessid, None)
        if consumer:
            consumer.kill()
            del self._consumers[sessid]

        # Kill producers that no longer have a client
        self._clean_producers()

    def _clean_producers(self):
        """Deletes any producers that have no clients."""

        for terms in self._producers.keys():
            if terms not in self._terms.values():
                self._producers[terms].kill()
                del self._producers[terms]


class StreamRequest():
    """Helper class. Represents a socketio connection"""

    def __init__(self, socketio_request, data=None):
        """Retrieves the relevent information from the socketio request and msg data."""

        self.sessid = socketio_request.namespace.socket.sessid
        self.emit = socketio_request.namespace.emit
        self.tracking_terms = data['tracking'] if data else None
