from typing import Dict
import discord

from utils import get_all_message

message_cache: Dict[int, discord.Message] = {}


async def get_message(message_id: int, channel: discord.TextChannel) -> discord.Message | None:
    if message_id not in message_cache:
        message_cache[message_id] = await channel.fetch_message(message_id)

    return message_cache[message_id]


def remove_message(message_id: int) -> None:
    if message_id in message_cache:
        message_cache.pop(message_id)


def clear_cache() -> None:
    message_cache.clear()
