import datetime
import os
import discord
import icalendar # type: ignore
import pylev # type: ignore

import bump_bot_config as config
import discord_client
import found_reactions_cache

def create_calendar(date: datetime.date, start_time: datetime.time) -> icalendar.Calendar:
	cal = icalendar.Calendar()
	cal.add('prodid', '-//Bump Bot//Bump Bot//')
	cal.add('version', '2.0')

	event = icalendar.Event()
	event.add('summary', config.get_calendar_event_summary())
	event.add('dtstart', datetime.datetime.combine(date, start_time))
	event.add('dtend', datetime.datetime.combine(date, datetime.time(23,59,59)))
	event.add('dtstamp', datetime.datetime.now())
	cal.add_component(event)
	return cal

def find_closest_index(options: list[str], to_find: str) -> int:
	closest_distance = 99999
	closest_index = -1
	for index, option in enumerate(options):
		distance = pylev.levenshtein(option, to_find)
		if distance < closest_distance:
			closest_distance = distance
			closest_index = index
	return closest_index

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

#TODO: Refactor this and bump_message.py (into classes?) to avoid code duplication using the magic of functions and polymorphism
def get_embed_and_files(
		found_reactions: found_reactions_cache.FoundReactions,
		weekday: str,
		message_date: datetime.date) -> tuple[discord.Embed, list[discord.File]]:	

	weekday_index = find_closest_index(WEEKDAYS, weekday.lower())
	date = message_date + datetime.timedelta(weekday_index - message_date.weekday())
	if weekday_index < message_date.weekday():
		date += datetime.timedelta(7)

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
	earliest_possible_time = ""
	for reaction in config.get_bump_time_reactions():
		members = set()
		if reaction in found_reactions:
			members |= found_reactions[reaction]
		members -= found_members
		
		if len(members) > 0:
			found_members |= members	
			if len(found_members) == len(members_who_voted):
				earliest_possible_time = config.get_bump_time_reactions()[reaction]
				message_text += "**Earliest possible time: {}**\n\n".format(earliest_possible_time)

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
	embed = discord.Embed(title=config.get_bump_time_embed_title().format()).add_field(
		name=config.get_bump_time_embed_field_name(),
		value=message_text)
	files = []

	if len(members_who_voted) >= config.get_required_votes():
		start_time = datetime.time.fromisoformat(earliest_possible_time)

		os.makedirs(os.path.dirname(config.get_calendar_file_name()), exist_ok=True)
		with open(config.get_calendar_file_name(), 'wb') as f:
			f.write(create_calendar(date, start_time).to_ical())
		
		files.append(discord.File(config.get_calendar_file_name()))
	
	return (embed, files)

async def send(channel: discord.TextChannel, argument: str) -> discord.Message:
	content = config.get_bump_time_message_content_prefix() + argument + config.get_bump_time_message_content_postfix()
	embed, files = get_embed_and_files({}, argument, datetime.date.today())
	message: discord.Message = await channel.send(content, embed=embed, files=files)	
	for reaction in config.get_bump_time_reactions():
		emoji = discord_client.get_emoji(reaction)
		if emoji is not None:
			await message.add_reaction(emoji) # Await here because order is important
	found_reactions_cache.initialize_found_reactions(message, config.get_bump_time_reactions())
	return message


async def update(message: discord.Message) -> discord.Message:
	argument = message.content[len(config.get_bump_time_message_content_prefix()):-len(config.get_bump_time_message_content_postfix())]
	reactions = await found_reactions_cache.get_found_reactions(message, config.get_bump_time_reactions())
	embed, files = get_embed_and_files(reactions, argument, message.created_at.date())
	return await message.edit(embed=embed, attachments=files)

def handles(message: discord.Message) -> bool:
	return bool(message.content.startswith(config.get_bump_time_message_content_prefix())
	     and message.content.endswith(config.get_bump_time_message_content_postfix()))