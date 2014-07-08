from flask import Flask, render_template, session
from flask.ext.socketio import SocketIO, request
from twitter_dash import StreamConsumer, StreamProducer
import json


# Setup the app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'some bologna secret key' # Secret key used for the session module (can identify unique users; built on top of cookies)
socketio =  SocketIO(app)
MAX_INSTANCES_PER_USER = 3



# Globals used to keep track of Consumer/Producer services
_producers = {}        	# Stores each Producer service
_consumers = {}        	# Stores each user's Consumer service
_namespaces = {}		# Stores each user's namespace (used for the socket location)


def _create_producer():
    """Creates a new Producer stream for the terms specified in tracking."""

    # Get user's tracking terms and username
    tracking = session['tracking']
    terms = frozenset(tracking)
    user = session['username']

    print _producers

    # Remove this client from other streams
    for p_terms, producer in _producers.iteritems():
        if user in producer.clients:
            if producer.tracking is not tracking:
                producer.remove_client(user)

    # Create a new producer if it doesn't exist or it has been killed.
    if terms not in _producers or _producers[terms].value:
        # Create a Twitter stream Producer (that filters on the term 'tracking')
        feed_producer = StreamProducer(tracking)
        feed_producer.start()
        _producers[terms] = feed_producer

    # Add this user to the client list
    _producers[terms].add_client(user)


def _create_consumer():
    """Creates a new redis pub/sub consumer that subscribes to correct channel."""

    # Get user information
    tracking = session['tracking']
    username = session['username']
    emit = _namespaces[username].emit

    # Kill previous consumer (each user only gets one instance)
    if username in _consumers:
    	_consumers[username].kill()

	# Create new Consumer
    channel = json.dumps(sorted(tracking))
    feed_consumer = StreamConsumer(channel, emit)
    feed_consumer.start()
    _consumers[username] = feed_consumer

def _kill_stream():
    """Kills the current user's Twitter consumer."""

    user = session['username']
    consumer = _consumers.get(user, None)
    terms = frozenset(session['tracking'])
    producer = _producers.get(terms, None)

    if consumer:
        consumer.kill()
        del _consumers[user]

    if producer:
        producer.remove_client(user)


@app.before_request
def setup():
    """Adds a username to the session object."""
    session['username'] = request.remote_addr
    print "Recieved new request. IP: ", session['username']


@app.route('/')
def index():
    """Sets up the user's Twitter feed Producer."""

    # See if user has multiple tabs open (using our service)
    instance_count = len(session.get('sessids', []))
    if instance_count > MAX_INSTANCES_PER_USER:
        return render_template('sorry.html')

    # Return index.html (will begin the socket.io connection)
    return render_template('index.html')


@socketio.on('connect', namespace='/twitter')
def on_connect():
    """Saves the socketio namespace context."""

    print "Connected to a socket. sessid: ", request.namespace.socket.sessid

    # Save user namespace (used to get the socketio emit function)
    _namespaces[session['username']] = request.namespace

@socketio.on('start-stream', namespace='/twitter')
def on_start_stream(msg):
    """Starts a twitter stream with the terms specifed in the client message."""

    print "starting stream"
    # Set the session tracking items
    tracking = msg['tracking']
    session['tracking'] = tracking

    # Create a new Twitter stream Producer/Consumer
    _create_producer()
    _create_consumer()

@socketio.on('pause-stream', namespace='/twitter')
def on_pause_stream():
    """Kills the current Twitter stream."""

    print "Pausing Twitter stream."
    # Kill Consumer
    _kill_stream()


@socketio.on('disconnect', namespace='/twitter')
def on_disconnect():
    """Kills the associated Twitter feed Consumer and Producer if no other clients exist."""

    # TODO: There seem to be intermittent disconnect calls that do not actually
    # result in the client disconnecting. For example, when the tracking page is open,
    # this callback is called, on_connect [I believe] is NOT called, and the client
    # still receives Tweets. This should not happen.
    print "Entered a disconnect."
    _kill_stream()


if __name__ == '__main__':
    # Run the web service
    socketio.run(app)
