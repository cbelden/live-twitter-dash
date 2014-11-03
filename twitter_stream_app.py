from flask import Flask, send_from_directory
from flask.ext.socketio import SocketIO, request
from twitter_stream import StreamServer, StreamRequest, DebugStreamProducer
import logging


# Setup logging
logging.basicConfig(level=logging.DEBUG)


# Setup the app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'some bologna secret key' # Secret key used for flask sessions. Use actual key in production.
socketio =  SocketIO(app)
MAX_INSTANCES_PER_USER = 3


# Global stream manager to handle the socketio requests
stream_server = StreamServer()


@app.route('/')
def index():
    """Delivers client pay-load."""
    return send_from_directory('templates', 'index.html')


@socketio.on('connect', namespace='/twitter')
def on_connect():
    """Called when a client opens a socketio conneciton."""
    logging.debug('New socketio connection: ' + request.namespace.socket.sessid)


@socketio.on('start-stream', namespace='/twitter')
def on_start_stream(msg):
    """Starts a twitter stream with the terms specifed in the client message."""
    logging.info('Received a "play" request: ' + request.namespace.socket.sessid)
    stream_request = StreamRequest(request, msg)
    stream_server.spawn_stream(stream_request)


@socketio.on('pause-stream', namespace='/twitter')
def on_pause_stream(msg):
    """Kills the current Twitter stream."""
    logging.info('Received a "pause" request: ' + request.namespace.socket.sessid)
    stream_request = StreamRequest(request)
    stream_server.kill_connection(stream_request)


@socketio.on('disconnect', namespace='/twitter')
def on_disconnect():
    """Kills the associated Twitter feed Consumer and Producer if no other clients exist."""
    logging.info('Disconnected from the socketio connection: ' + request.namespace.socket.sessid)
    stream_request = StreamRequest(request)
    stream_server.kill_connection(stream_request)


if __name__ == '__main__':
    # Run the web service (for debugging only)
    socketio.run(app)
