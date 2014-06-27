import tweepy
import os
import redis
import json
import time
import gevent


class CustomStreamListener(tweepy.StreamListener):
	"""Listens to a twitter stream and publishes tweets to redis."""

	def __init__(self):
		"""Gets redis instance."""

		self._redis = redis.Redis()

		# Call StreamListener constructor
		super(CustomStreamListener, self).__init__()

	def on_status(self, status):
		"""Publishes the Tweet to redis."""

		# Get text
		text = status.text.encode('utf8')

		# Get user profile photo
		user = status.user
		screen_name = user.screen_name
		img_url = user.profile_image_url

		# Publish the data
		data = {'text': text,
				'user_image_url': img_url,
				'screen_name': screen_name}
		self._redis.publish('twitter-data', json.dumps(data))

		# Throttle our results
		time.sleep(1)

class TwitterFeedProducer(gevent.Greenlet):
	"""Defines a Greenlet that publishes twitter data to redis."""
	
	def __init__(self, track):
		"""Creates instance of CustomStreamListener."""

		self._stream_listener = CustomStreamListener()
		self._tracking = track

		# Call gevent.Greenlet constructor
		super(TwitterFeedProducer, self).__init__()

	def _run(self):
		"""Starts the twitter stream listener/redis-publisher."""

		# Authorize tweepy
		consumer_key = os.environ['TWITTER_CONSUMER_KEY']
		consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
		access_token = os.environ['TWITTER_ACCESS_TOKEN']
		access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
		oauth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		oauth.set_access_token(access_token, access_token_secret)

		# Listen to the stream of tweets containing the words/hashtags in 'filtering'
		stream = tweepy.Stream(oauth, self._stream_listener)
		stream.filter(track=self._tracking)
