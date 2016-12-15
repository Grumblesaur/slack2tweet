# James Murphy
# CPSC 470 / IT Infrastructure in the Cloud
# Final Project / slack2tweet bot

import os
import time
import tweepy
from slackclient import SlackClient
from random import randrange
from secret import *

bot_name = 'slack2tweet'
my_url = 'https://twitter.com/Grumblesaur'

def tweet(slack, tw_api, message, username):
	tokens = message.split()
	if tokens[0].lower() == bot_name and tokens[1].lower() == 'tweet':
		tweet = ("%s: %s" % (username, ' '.join(tokens[2:])))[:140]
		print tweet
		tw_api.update_status(status=tweet)
		return tweet[len(username)+2:140]

def recent(slack, tw_api, message):
	tokens = message.split()
	if tokens[0].lower() == bot_name and tokens[1] == 'recent':
		tweet = tw_api.user_timeline()[randrange(0,20)]
		print tweet
		return "%s %stweeted '%s' recently." % (
			tweet.author.name,
			('','re')[tweet.retweeted],
			tweet.text
		)

def find(slack, tw_api, message):
	tokens = message.split()
	if tokens[0].lower() == bot_name and tokens[1] == 'find':
		user = tw_api.get_user(tokens[2])
		print user
		return "Twitter user '%s' (ID:%s) has %s tweets." % (
			user.name,
			user.id,
			user.statuses_count
		)

def who(slack, tw_api, message):
	tokens = message.split()
	if tokens[0].lower() == bot_name and tokens[1] == 'who':
		user = tw_api.me()
		print user
		return "Twitter user '%s' created me." % (user.name,)

def help_(slack, tw_api, message):
	tokens = message.split()
	if tokens[0].lower() == bot_name and tokens[1] == 'help':
		print 'help'
		return "slack2tweet %s" % (
			"[tweet <message>, recent, find <username>, who, help]",
		)

def main(): 
	t_auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	t_auth.set_access_token(access_token, access_secret)
	api = tweepy.API(t_auth)
	sc = SlackClient(slack_token)
	
	if sc.rtm_connect():
		while True:
			for datum in sc.rtm_read():
				print datum
				msg = datum.get("text")
				usr = datum.get("user")
				usr = sc.api_call(
					"users.info",
					user=usr,
					token=slack_token
				).get(u'user')
				try:
					usr = usr.get(u'name')
				except AttributeError as e:
					print e
					usr = None
				print type(usr)
				print 'usr =', usr
				print
				if not (msg and usr): # look, de Morgan's law in the wild
					continue
				try:
					success = tweet(sc, api, msg, usr)
					recent_post = recent(sc, api, msg)
					found_user = find(sc, api, msg)
					creator = who(sc, api, msg)
					help_msg = help_(sc, api, msg)
				except Exception as e:
					print e
				if success:
					sc.api_call('chat.postMessage',
						channel='testing',
						text="User <@%s> posted '%s' to %s" % (
							usr,
							success,
							my_url
						),
						as_user=True,
						token=slack_token,
					)
				if recent_post:
					sc.api_call('chat.postMessage',
						channel='testing',
						text=recent_post,
						as_user=True,
						token=slack_token
					)
				if found_user:
					sc.api_call('chat.postMessage',
						channel='testing',
						text=found_user,
						as_user=True,
						token=slack_token
					)
				if creator:
					sc.api_call('chat.postMessage',
						channel='testing',
						text=creator,
						as_user=True,
						token=slack_token
					)
				if help_msg:
					sc.api_call('chat.postMessage',
						channel='testing',
						text=help_msg,
						as_user=True,
						token = slack_token
					)
			time.sleep(0.5)

main()	
