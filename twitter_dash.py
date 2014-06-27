from flask import Flask, render_template
from flask.ext.socketio import SocketIO, request
from twitter_dash import Consumer, TwitterFeedProducer


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret' # TODO: find out what this is used for
socketio =  SocketIO(app)


@app.route('/')
def index():
	"""Renders index.html."""
	return render_template('index.html', filtering='usa')

@socketio.on('connect', namespace='/twitter')
def on_connect():
	"""Called when a socketio connection is made with the browser."""

	# Get request namespace
	namespace = request.namespace

	# Spawn Twitter consumer
	twitter_consumer = Consumer('twitter-data', namespace.emit)
	twitter_consumer.start()

@socketio.on('filter-request', namespace='/twitter')
def on_filter_request(msg):
	"""Called when a new filter is requeste."""
	# TODO - kill current twitter feed producer and start a new one.
	pass


if __name__ == '__main__':

	# Start the twitter producer
	producer = TwitterFeedProducer(['usa'])
	producer.start()

	# Run the web service
	socketio.run(app)
