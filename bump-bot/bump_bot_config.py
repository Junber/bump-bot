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


def get_config() -> dict[str, Any]:
    if len(config) == 0:
        load_config()
    return config


class BasicCommandConfig:
    config: dict[str, Any] = {}

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    def get_trigger(self) -> str:
        return self.config.get("trigger", "")

    def get_channel_name(self) -> str:
        return self.config.get("channel", "")

    def get_message_content(self) -> str:
        return self.config.get("message content", "")


# Voting
def get_voting() -> dict[str, Any]:
    return get_config().get("voting", {})


def get_voting_trigger() -> str:
    return get_voting().get("trigger", "")


def get_voting_channel_name() -> str:
    return get_voting().get("channel", "")


def get_required_votes() -> int:
    return get_voting().get("required votes", 0)


def get_voting_cancel_reaction() -> str:
    return get_voting().get("cancel reaction", "")


# Cards
def get_cards() -> BasicCommandConfig:
    return BasicCommandConfig(get_config().get("cards", {}))


# Voting::Bump message
def get_bump_message_config() -> dict[str, Any]:
    return get_voting().get("bump message", {})


def get_bump_message_content() -> str:
    return get_bump_message_config().get("message content", "")


def get_bump_embed_title() -> str:
    return get_bump_message_config().get("embed title", "")


def get_bump_embed_field_name() -> str:
    return get_bump_message_config().get("embed field name", "")


def get_bump_reactions() -> dict[str, str]:
    return get_bump_message_config().get("reactions", {})


# Voting::Bump time message
def get_bump_time_message_config() -> dict[str, Any]:
    return get_voting().get("bump time message", {})


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


def get_bump_time_in_person_reaction() -> str:
    return get_bump_time_message_config().get("in-person reaction", "")


def get_bump_time_in_person_days() -> list[str]:
    return get_bump_time_message_config().get("in-person days", [])


def get_default_calendar_event_summary() -> str:
    return get_bump_time_message_config().get("default calendar event summary", "")


def get_in_person_calendar_event_summary() -> str:
    return get_bump_time_message_config().get("in-person calendar event summary", "")


# Logging
def get_logging() -> dict[str, Any]:
    return get_config().get("logging", {})


def get_log_file_name() -> str:
    return get_logging().get("log file name", "")


def get_log() -> BasicCommandConfig:
    return BasicCommandConfig(get_logging())


# Shutdown
def get_shutdown() -> BasicCommandConfig:
    return BasicCommandConfig(get_config().get("shutdown", {}))


# Clear cache
def get_clear_cache() -> BasicCommandConfig:
    return BasicCommandConfig(get_config().get("clear cache", {}))


# Bookstack
def get_bookstack() -> dict[str, Any]:
    return get_config().get("bookstack", {})


def get_bookstack_channel_name() -> str:
    return get_bookstack().get("channel", "")


def get_bookstack_trigger() -> str:
    return get_bookstack().get("trigger", "")


def get_bookstack_exported_emoji() -> str:
    return get_bookstack().get("exported emoji", "")


# Bookstack::Export All
def get_bookstack_export_all() -> BasicCommandConfig:
    return BasicCommandConfig(get_bookstack().get("export all", {}))


# Bookstack::Export All
def get_bookstack_unexport_all() -> BasicCommandConfig:
    return BasicCommandConfig(get_bookstack().get("unexport all", {}))


# Bookstack::Clear emoji
def get_bookstack_clear_emoji() -> BasicCommandConfig:
    return BasicCommandConfig(get_bookstack().get("clear emoji", {}))
