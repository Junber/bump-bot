import logging
import os
import discord

import config

client = None

def get_client():
	global client
	if not client:
		intents = discord.Intents.default()
		intents.message_content = True
		intents.members = True
		client = discord.Client(intents=intents)
		
	return client

def run_client():
	handler = None
	log_file_name = config.get_log_file_name()
	if len(log_file_name) > 0:
		os.makedirs(os.path.dirname(log_file_name), exist_ok=True)
		handler = logging.FileHandler(filename=log_file_name, encoding='utf-8', mode='w')
	get_client().run(config.get_token(), log_handler=handler, log_level=logging.DEBUG)

def get_emoji(emoji_string: str):
	if emoji_string[0].isalpha():
		return discord.utils.get(get_client().emojis, name=emoji_string)
	return emoji_string