from flask import Flask, render_template
from flask.ext.socketio import SocketIO, request
from twitter_stream import StreamServer, StreamRequest


# Setup the app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'some bologna secret key' # Secret key used for flask sessions. Use actual key in production.
socketio =  SocketIO(app)
MAX_INSTANCES_PER_USER = 3


# Global stream manager to handle the socketio requests
stream_server = StreamServer()


@app.before_request
def setup():
    """Adds a userid to the session object."""
    pass


@app.route('/')
def index():
    """Sets up the user's Twitter feed Producer."""

    return render_template('index.html')


@socketio.on('connect', namespace='/twitter')
def on_connect():
    """Called when a client opens a socketio conneciton."""
    print ">>>> connected to client"


@socketio.on('start-stream', namespace='/twitter')
def on_start_stream(msg):
    """Starts a twitter stream with the terms specifed in the client message."""

    stream_request = StreamRequest(request, msg)
    stream_server.spawn_stream(stream_request)


@socketio.on('pause-stream', namespace='/twitter')
def on_pause_stream():
    """Kills the current Twitter stream."""

    stream_request = StreamRequest(request)
    stream_server.kill_connection(stream_request)


@socketio.on('disconnect', namespace='/twitter')
def on_disconnect():
    """Kills the associated Twitter feed Consumer and Producer if no other clients exist."""

    stream_request = StreamRequest(request)
    stream_server.kill_connection(stream_request)


if __name__ == '__main__':
    # Run the web service
    socketio.run(app)
