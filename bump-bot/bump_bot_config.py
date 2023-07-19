from collections import OrderedDict
import json
import os
from typing import Any

config: dict[str, Any] = {}
token = ""

def load_config() -> None:
	if os.path.exists("config/config.json"):
		with open("config/config.json", "r", encoding="utf-8") as config_file:
			global config
			config = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(config_file.read())
		
	if os.path.exists("config/token.txt"):
		with open("config/token.txt", "r") as token_file:
			global token
			token = token_file.readline()

def get_token() -> str:
	return token

# General
def get_trigger() -> str:
	return config.get("trigger", "")

def get_channel_name() -> str:
	return config.get("channel", "")

def get_required_votes() -> int:
	return config.get("required votes", 0)

def get_log_file_name() -> str:
	return config.get("log file name", "")

def get_admin_channel_name() -> str:
	return config.get("admin channel", "")

def get_shutdown_trigger() -> str:
	return config.get("shutdown trigger", "")

def get_log_trigger() -> str:
	return config.get("log trigger", "")


# Bump message
def get_bump_message_config() -> dict[str, Any]:
	return config.get("bump message", {})

def get_bump_message_content() -> str:
	return get_bump_message_config().get("message content", "")

def get_bump_embed_title() -> str:
	return get_bump_message_config().get("embed title", "")

def get_bump_embed_field_name() -> str:
	return get_bump_message_config().get("embed field name", "")

def get_bump_reactions() -> dict[str, str]:
	return get_bump_message_config().get("reactions", {})


# Bump time message
def get_bump_time_message_config() -> dict[str, Any]:
	return config.get("bump time message", {})

def get_bump_time_message_content_prefix() -> str:
	return get_bump_time_message_config().get("message content prefix", "")

def get_bump_time_message_content_postfix() -> str:
	return get_bump_time_message_config().get("message content postfix", "")

def get_bump_time_embed_title() -> str:
	return get_bump_time_message_config().get("embed title", "")

def get_bump_time_embed_field_name() -> str:
	return get_bump_time_message_config().get("embed field name", "")

def get_bump_time_reactions() -> dict[str, str]:
	return get_bump_time_message_config().get("reactions", {})