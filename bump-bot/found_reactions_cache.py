from typing import List
import discord

import bump_bot_config as config
import discord_client

ToBeFoundReactions = dict[str, str]
FoundReactions = dict[str, set[discord.Member]]

found_reactions_cache: dict[int, FoundReactions] = {}

def get_emoji_string(emoji: discord.PartialEmoji | discord.Emoji |str) -> str:
	if not isinstance(emoji, str):
		return "{}".format(emoji.name)
	return emoji

async def get_found_reactions(message: discord.Message, reactions: ToBeFoundReactions) -> FoundReactions:
	if message.id in found_reactions_cache:
		return found_reactions_cache[message.id]

	found_reactions = {}
	for reaction in message.reactions:
		emoji_string = get_emoji_string(reaction.emoji)
		if emoji_string in reactions:
			users = [user async for user in reaction.users()]
			user = discord_client.get_client().user
			if user is not None:
				users.remove(user) # type: ignore
			found_reactions[emoji_string] = set(users)
	
	found_reactions_cache[message.id] = found_reactions
	return found_reactions

def initialize_found_reactions(message: discord.Message, reactions: ToBeFoundReactions) -> None:
	found_reactions: dict[str, set[discord.Member]] = {}
	for emoji_string in reactions:
		found_reactions[emoji_string] = set()
	found_reactions_cache[message.id] = found_reactions

def add_found_reaction(message_id: int, emoji: discord.PartialEmoji, member: discord.Member) -> None:
	if message_id in found_reactions_cache:
		found_reactions_cache[message_id][emoji.name].add(member)

def remove_found_reaction(message_id: int, emoji: discord.PartialEmoji, member: discord.Member) -> None:
	if message_id in found_reactions_cache:
		found_reactions_cache[message_id][emoji.name].remove(member)