import asyncio
from typing import Dict, List
import discord

import bump_bot_config as config
import discord_client
import found_reactions_cache

def get_embed(found_reactions: found_reactions_cache.FoundReactions) -> discord.Embed:
	members_who_voted = set()
	for reaction in found_reactions:
		members_who_voted |= found_reactions[reaction]

	message_text = "Current Voters: "

	if len(members_who_voted) == 0:
		message_text += "No votes yet"
	else:
		member : discord.Member
		for member in sorted(members_who_voted, key=lambda x: x.display_name):
			message_text += member.display_name
			message_text += ", "
		message_text = message_text.removesuffix(", ")
	
	message_text += " "

	if len(members_who_voted) >= config.get_required_votes():
		message_text += ":white_check_mark:"
	else:
		message_text += ":x:"

	message_text += "\n"

	for reaction in config.get_bump_reactions():
		members = set()
		if reaction in found_reactions:
			members = found_reactions[reaction]

		if len(members) == len(members_who_voted):
			message_text += ":white_check_mark:"
		else:
			message_text += ":x:"

		message_text += " {} ({}): ".format(config.get_bump_reactions()[reaction], discord_client.get_emoji(reaction))


		if len(members) == 0:
			message_text += "No one"
		elif len(members) < len(members_who_voted):
			for member in sorted(members, key=lambda x: x.display_name):
				message_text += member.display_name
				message_text += ", "
			message_text = message_text.removesuffix(", ")
		elif len(members) == len(members_who_voted):
			message_text += "Everyone!" 

		message_text += '\n'
	
	return discord.Embed(title=config.get_bump_embed_title()).add_field(name=config.get_bump_embed_field_name(), value=message_text)

async def send(channel: discord.TextChannel) -> discord.Message:
	message: discord.Message = await channel.send(config.get_bump_message_content(), embed=get_embed({}))	
	for reaction in config.get_bump_reactions():
		emoji = discord_client.get_emoji(reaction)
		if emoji is not None:
			await message.add_reaction(emoji) # Await here because order is important
	found_reactions_cache.initialize_found_reactions(message, config.get_bump_reactions())
	return message


async def update(message: discord.Message) -> discord.Message:
	return await message.edit(embed=get_embed(await found_reactions_cache.get_found_reactions(message, config.get_bump_reactions())))

def handles(message: discord.Message) -> bool:
	return bool(message.content == config.get_bump_message_content())