import tweepy
import os


# Authorize tweepy
consumer_key = os.environ['TWITTER_CONSUMER_KEY']
consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
access_token = os.environ['TWITTER_ACCESS_TOKEN']
access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
oauth = tweepy.OAuthHandler(consumer_key, consumer_secret)
oauth.set_access_token(access_token, access_token_secret)