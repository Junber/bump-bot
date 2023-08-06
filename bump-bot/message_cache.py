from typing import Dict
import discord

from utils import get_all_message

message_cache: Dict[int, discord.Message] = {}


async def get_message(message_id: int, channel: discord.TextChannel) -> discord.Message | None:
    if message_id in message_cache:
        return message_cache[message_id]

    async for message in get_all_message(channel):
        message_cache[message.id] = message
        if message.id == message_id:
            return message

    return None
