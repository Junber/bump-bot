import asyncio
from typing import Iterable, Tuple
import discord

import discord_client

ToBeFoundReactions = Iterable[str]
FoundReactions = dict[str, set[discord.Member]]

found_reactions_cache: dict[int, FoundReactions] = {}
found_reactions_cache_without_client: dict[int, FoundReactions] = {}

cache_lock = asyncio.Lock()


def get_emoji_string(emoji: discord.PartialEmoji | discord.Emoji | str) -> str:
    if not isinstance(emoji, str):
        return emoji.name
    return emoji


async def query_reactions(message: discord.Message) -> Tuple[FoundReactions, FoundReactions]:
    found_reactions: FoundReactions = {}
    found_reactions_without_client: FoundReactions = {}

    client_user = discord_client.get_client().user
    for reaction in message.reactions:
        emoji_string = get_emoji_string(reaction.emoji)
        users = [user async for user in reaction.users() if isinstance(user, discord.Member)]
        found_reactions[emoji_string] = set(users)
        if client_user is not None and client_user in users:
            users.remove(client_user)  # type: ignore
        found_reactions_without_client[emoji_string] = set(users)

    return (found_reactions, found_reactions_without_client)


async def get_found_reactions(
    message: discord.Message, include_client: bool = False
) -> FoundReactions:
    async with cache_lock:
        if include_client:
            if message.id in found_reactions_cache:
                return found_reactions_cache[message.id]
        else:
            if message.id in found_reactions_cache_without_client:
                return found_reactions_cache_without_client[message.id]

        (
            found_reactions_cache[message.id],
            found_reactions_cache_without_client[message.id],
        ) = await query_reactions(message)

        if include_client:
            return found_reactions_cache[message.id]
        else:
            return found_reactions_cache_without_client[message.id]


async def add_found_reaction(
    message_id: int, emoji: discord.PartialEmoji, member: discord.Member
) -> None:
    async with cache_lock:
        if message_id in found_reactions_cache:
            if emoji.name in found_reactions_cache[message_id]:
                found_reactions_cache[message_id][emoji.name].add(member)
            else:
                found_reactions_cache[message_id][emoji.name] = set([member])

            if member != discord_client.get_client().user:
                if emoji.name in found_reactions_cache_without_client[message_id]:
                    found_reactions_cache_without_client[message_id][emoji.name].add(member)
                else:
                    found_reactions_cache_without_client[message_id][emoji.name] = set([member])


async def remove_found_reaction(
    message_id: int, emoji: discord.PartialEmoji, member: discord.Member
) -> None:
    async with cache_lock:
        if (
            message_id in found_reactions_cache
            and member in found_reactions_cache[message_id][emoji.name]
        ):
            found_reactions_cache[message_id][emoji.name].remove(member)
            if member != discord_client.get_client().user:
                found_reactions_cache_without_client[message_id][emoji.name].remove(member)


async def initialize_empty_reactions(message_id: int) -> None:
    async with cache_lock:
        found_reactions_cache[message_id] = {}
        found_reactions_cache_without_client[message_id] = {}
