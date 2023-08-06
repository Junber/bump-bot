from typing import Iterable
import discord

import discord_client

ToBeFoundReactions = Iterable[str]
FoundReactions = dict[str, set[discord.Member]]

found_reactions_cache: dict[int, FoundReactions] = {}
found_reactions_cache_without_client: dict[int, FoundReactions] = {}


def get_emoji_string(emoji: discord.PartialEmoji | discord.Emoji | str) -> str:
    if not isinstance(emoji, str):
        return emoji.name
    return emoji


async def get_found_reactions(
    message: discord.Message, include_client: bool = False
) -> FoundReactions:
    if include_client:
        if message.id in found_reactions_cache:
            return found_reactions_cache[message.id]
    else:
        if message.id in found_reactions_cache_without_client:
            return found_reactions_cache_without_client[message.id]

    client_user = discord_client.get_client().user

    found_reactions: FoundReactions = {}
    found_reactions_without_client: FoundReactions = {}
    for reaction in message.reactions:
        emoji_string = get_emoji_string(reaction.emoji)
        users = [user async for user in reaction.users() if isinstance(user, discord.Member)]
        found_reactions[emoji_string] = set(users)
        if client_user is not None and client_user in users:
            users.remove(client_user)  # type: ignore
        found_reactions_without_client[emoji_string] = set(users)

    found_reactions_cache[message.id] = found_reactions
    found_reactions_cache_without_client[message.id] = found_reactions_without_client

    if include_client:
        return found_reactions
    else:
        return found_reactions_without_client


def add_found_reaction(
    message_id: int, emoji: discord.PartialEmoji, member: discord.Member
) -> None:
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


def remove_found_reaction(
    message_id: int, emoji: discord.PartialEmoji, member: discord.Member
) -> None:
    if message_id in found_reactions_cache:
        found_reactions_cache[message_id][emoji.name].remove(member)
        if member != discord_client.get_client().user:
            found_reactions_cache_without_client[message_id][emoji.name].remove(member)
