from stream_consumer import StreamConsumer
from stream_producer import StreamProducer
import json


class StreamManager():
    """Manages the stream producers/clients."""

    def __init__(self):
        """Initializes the StreamManager object."""

        self._producers = {}        # Pool of producers
        self._consumers = {}        # Each socketio session's consumer
        self._clients = {}          # Stores the sessid of each socketio client


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
        stream_consumer = StreamConsumer(channel, emit)

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
            feed_producer = StreamProducer(tracking_terms)
            feed_producer.start()
            self._producers[terms] = feed_producer

        # Add this sessid to the current client store
        if not terms in self._clients:
            self._clients[terms] = []

        self._clients[terms].append(sessid)

    def kill_connection(self, socketio_conn):
        """
        Kills the stream consumer specified by the userid and tracking terms, removes
        the connection from the dict of clients, and kills the stream producer if this
        is its last client.
        """

        sessid = socketio_conn.sessid
        tracking_terms = self._get_tracking_terms(sessid)  
        terms = frozenset(tracking_terms) if tracking_terms else None

        # Get this connection's consumer/producer
        consumer = self._consumers.get(sessid, None)
        producer = self._producers.get(terms, None)

        # Remove the sessid from the clients dict
        if terms:
            self._clients[terms].remove(sessid)

        # Kill/Delete the consumer
        if consumer:
            consumer.kill()
            del self._consumers[sessid]

        # Delete producer if there are no more clients
        if producer:

            if len(self._clients[terms]) < 1:
                producer.kill()
                del self._producers[terms]

    def _get_tracking_terms(self, sessid):
        """
        Queries the _clients dictionary for the terms that this socketio connection
        is subscribed to.
        """

        for terms, ids in self._clients.iteritems():

            if sessid in ids:
                return terms


class StreamRequest():
    """Helper class. Represents a socketio connection"""

    def __init__(self, socketio_request, data=None):
        """Retrieves the relevent information from the socketio request and msg data."""

        self.sessid = socketio_request.namespace.socket.sessid
        self.emit = socketio_request.namespace.emit
        self.tracking_terms = data['tracking'] if data else None
