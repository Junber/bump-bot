from collections import OrderedDict
import json
import os

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

def get_trigger():
	return config.get("trigger", "")

def get_embed_title():
	return config.get("embed title", "")

def get_embed_field_name():
	return config.get("embed field name", "")

def get_reactions():
	return config.get("reactions", {})

def get_channel_name():
	return config.get("channel", "")

def get_required_votes():
	return config.get("required votes", 0)