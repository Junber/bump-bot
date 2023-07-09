from collections import OrderedDict
import json
import os
import sys

config = {}
token = ""

def load_config():
	if os.path.exists("config/config.json"):
		with open("config/config.json", "r", encoding="utf-8") as config_file:
			global config
			config = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(config_file.read())
		
	if os.path.exists("config/token.txt"):
		with open("config/token.txt", "r") as token_file:
			global token
			token = token_file.readline()

def get_token():
	return token

# General
def get_trigger():
	return config.get("trigger", "")

def get_channel_name():
	return config.get("channel", "")

def get_required_votes():
	return config.get("required votes", 0)

def get_log_file_name():
	return config.get("log file name", "")

def get_admin_channel_name():
	return config.get("admin channel", "")

def get_shutdown_trigger():
	return config.get("shutdown trigger", "")

def get_log_trigger():
	return config.get("log trigger", "")


# Bump message
def get_bump_message_config():
	return config.get("bump message", {})

def get_bump_message_content():
	return get_bump_message_config().get("message content", "")

def get_bump_embed_title():
	return get_bump_message_config().get("embed title", "")

def get_bump_embed_field_name():
	return get_bump_message_config().get("embed field name", "")

def get_bump_reactions():
	return get_bump_message_config().get("reactions", {})


# Bump time message
def get_bump_time_message_config():
	return config.get("bump time message", {})

def get_bump_time_message_content_prefix():
	return get_bump_time_message_config().get("message content prefix", "")

def get_bump_time_message_content_postfix():
	return get_bump_time_message_config().get("message content postfix", "")

def get_bump_time_embed_title():
	return get_bump_time_message_config().get("embed title", "")

def get_bump_time_embed_field_name():
	return get_bump_time_message_config().get("embed field name", "")

def get_bump_time_reactions():
	return get_bump_time_message_config().get("reactions", {})