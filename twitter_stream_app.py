from flask import Flask, render_template, jsonify
from flask.ext.socketio import SocketIO, request
from twitter_stream import StreamServer, StreamRequest, trending_terms
import logging


# Setup logging
logging.basicConfig(level=logging.DEBUG)


# Setup the app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'some bologna secret key' # Secret key used for flask sessions. Use actual key in production.
socketio =  SocketIO(app)


# Global stream manager to handle the socketio requests
stream_server = StreamServer()


@app.route('/')
def index():
    """Delivers client pay-load."""
    return render_template('index.html')

@app.route('/trending-terms')
def trending():
    """Returns a list of the trending terms on Twitter in the US."""
    return jsonify(results=[{'term': t} for t in trending_terms()])


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
def on_pause_stream():
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
