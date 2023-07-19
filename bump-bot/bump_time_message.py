import discord

import bump_bot_config as config
import discord_client
import found_reactions_cache

#TODO: Refactor this and bump_message.py (into classes?) to avoid code duplication using the magic of functions and polymorphism
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

	found_members: set[discord.Member] = set()	
	message_text_options_chunk = ""
	for reaction in config.get_bump_time_reactions():
		members = set()
		if reaction in found_reactions:
			members |= found_reactions[reaction]
		members -= found_members
		
		if len(members) > 0:
			found_members |= members	
			if len(found_members) == len(members_who_voted):
				message_text += "**Earliest possible time: {}**\n\n".format(config.get_bump_time_reactions()[reaction])

		message_text_options_chunk += " {} ({}): ".format(config.get_bump_time_reactions()[reaction], discord_client.get_emoji(reaction))


		if len(members) == 0:
			message_text_options_chunk += "-"
		elif len(members) < len(members_who_voted):
			for member in sorted(members, key=lambda x: x.display_name):
				message_text_options_chunk += member.display_name
				message_text_options_chunk += ", "
			message_text_options_chunk = message_text_options_chunk.removesuffix(", ")
		elif len(members) == len(members_who_voted):
			message_text_options_chunk += "Everyone!" 

		message_text_options_chunk += '\n'
	
	message_text += message_text_options_chunk
	return discord.Embed(title=config.get_bump_time_embed_title().format()).add_field(name=config.get_bump_time_embed_field_name(), value=message_text)

async def send(channel: discord.TextChannel, argument: str) -> discord.Message:
	content = config.get_bump_time_message_content_prefix() + argument + config.get_bump_time_message_content_postfix()
	message: discord.Message = await channel.send(content, embed=get_embed({}))	
	for reaction in config.get_bump_time_reactions():
		emoji = discord_client.get_emoji(reaction)
		if emoji is not None:
			await message.add_reaction(emoji) # Await here because order is important
	found_reactions_cache.initialize_found_reactions(message, config.get_bump_time_reactions())
	return message


async def update(message: discord.Message) -> discord.Message:
	return await message.edit(embed=get_embed(await found_reactions_cache.get_found_reactions(message, config.get_bump_time_reactions())))

def handles(message: discord.Message) -> bool:
	return bool(message.content.startswith(config.get_bump_time_message_content_prefix())
	     and message.content.endswith(config.get_bump_time_message_content_postfix()))