from typing import Dict
import discord

message_cache: Dict[int, discord.Message] = {}


async def get_replied(message: discord.Message) -> discord.Message:
    if (
        not message.reference
        or not message.reference.message_id
        or not isinstance(message.channel, discord.TextChannel)
    ):
        raise
    if message.reference.cached_message:
        return message.reference.cached_message
    return await get_message(message.reference.message_id, message.channel)


async def get_message(message_id: int, channel: discord.TextChannel) -> discord.Message:
    if message_id not in message_cache:
        message_cache[message_id] = await channel.fetch_message(message_id)

    return message_cache[message_id]


def remove_message(message_id: int) -> None:
    if message_id in message_cache:
        message_cache.pop(message_id)


def clear_cache() -> None:
    message_cache.clear()
