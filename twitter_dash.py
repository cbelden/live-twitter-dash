from flask import Flask, render_template
from flask.ext.socketio import SocketIO, request
from twitter_dash import Consumer, TwitterFeedProducer
from collections import namedtuple


app = Flask(__name__)
app.config['DEBUG'] = True
twitter_stream = {'track': None, 'producer': None}
app.config['SECRET_KEY'] = 'secret' # TODO: find out what this is used for
socketio =  SocketIO(app)


@app.route('/<tracking>')
def index(tracking):
	"""Renders index.html."""

	# Kill current twitter stream
	if twitter_stream['producer']:
		twitter_stream['producer'].kill()

	# Assign new twitter stream
	twitter_stream['track'] = tracking
	twitter_stream['producer'] = TwitterFeedProducer([tracking])

	# Start the twitter producer
	twitter_stream['producer'].start()

	print twitter_stream

	return render_template('index.html', track=tracking)

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


	# Run the web service
	socketio.run(app)
