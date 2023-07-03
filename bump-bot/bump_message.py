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
	members_who_voted = set()
	for reaction in found_reactions:
		members_who_voted = members_who_voted.union(found_reactions[reaction])

	message_text = "Current Voters: "

	if len(members_who_voted) == 0:
		message_text += "No votes yet"
	else:
		member : discord.Member
		for member in members_who_voted:
			message_text += member.display_name
			message_text += ", "
		message_text = message_text.removesuffix(", ")
	
	message_text += " "

	if len(members_who_voted) >= config.get_required_votes():
		message_text += ":white_check_mark:"
	else:
		message_text += ":x:"

	message_text += "\n"

	for reaction in config.get_reactions():
		members = []
		if reaction in found_reactions:
			members = found_reactions[reaction]

		if len(members) == len(members_who_voted):
			message_text += ":white_check_mark:"
		else:
			message_text += ":x:"

		message_text += " {} ({}): ".format(config.get_reactions()[reaction], get_emoji(reaction))


		if len(members) == 0:
			message_text += "No one"
		elif len(members) < len(members_who_voted):
			for member in members:
				message_text += member.display_name
				message_text += ", "
			message_text = message_text.removesuffix(", ")
		elif len(members) == len(members_who_voted):
			message_text += "Everyone!" 

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