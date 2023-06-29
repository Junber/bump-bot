import asyncio
from typing import Dict, List
import discord

import config
import discord_client
import found_reactions_cache

def get_emoji(emoji_string: str):
	if emoji_string[0].isalpha():
		return discord.utils.get(discord_client.get_client().emojis, name=emoji_string)
	return emoji_string

def bump_message_embed(found_reactions: found_reactions_cache.FoundReactions):
	users_who_voted = set()
	for reaction in found_reactions:
		users_who_voted = users_who_voted.union(found_reactions[reaction])

	message_text = "Current Voters: "

	if len(users_who_voted) == 0:
		message_text += "No votes yet"
	else:
		user : discord.User
		for user in users_who_voted:
			message_text += user.display_name
			message_text += ", "
		message_text = message_text.removesuffix(", ")
	
	message_text += " "

	if len(users_who_voted) >= config.get_required_votes():
		message_text += ":white_check_mark:"
	else:
		message_text += ":x:"

	message_text += "\n"

	for reaction in config.get_reactions():
		users = []
		if reaction in found_reactions:
			users = found_reactions[reaction]

		if len(users) == len(users_who_voted):
			message_text += ":white_check_mark:"
		else:
			message_text += ":x:"

		message_text += " {} ({}): ".format(config.get_reactions()[reaction], get_emoji(reaction))

		if len(users) == 0:
			message_text += "No one"
		else:
			for user in users:
				message_text += user.display_name
				message_text += ", "
			message_text = message_text.removesuffix(", ")

		message_text += '\n'
	
	return discord.Embed(title=config.get_embed_title()).add_field(name=config.get_embed_field_name(), value=message_text)

async def send_bump_message(channel: discord.TextChannel):
	message: discord.Message = await channel.send("bump", embed=bump_message_embed({}))	
	for reaction in config.get_reactions():
		await message.add_reaction(get_emoji(reaction)) # Await here because order is important
	found_reactions_cache.initialize_found_reactions(message)
	return message


async def update_bump_message(message: discord.Message):
	return await message.edit(embed=bump_message_embed(await found_reactions_cache.get_found_reactions(message)))