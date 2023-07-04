import asyncio
import functools
import sys
from typing import Any, Coroutine
import discord

import config
import discord_client
import message_cache
import found_reactions_cache
import bump_message
import bump_time_message

def main():
	config.load_config()
	client = discord_client.get_client()

	async def replace_pins(channel: discord.TextChannel, new_pin_function):
		async with asyncio.TaskGroup() as tg:
			for pinned in await channel.pins(): # TODO: Cache pins?
				tg.create_task(pinned.unpin())
			new_message = await new_pin_function()
			tg.create_task(new_message.pin())

	@client.event
	async def on_message(message: discord.Message):
		if message.author == client.user:
			return
		
		if message.channel.name == config.get_channel_name():
			if message.content == config.get_trigger():
				await replace_pins(message.channel, functools.partial(bump_message.send, message.channel))
			elif message.content.startswith(config.get_trigger()):
				argument = message.content[len(config.get_trigger()):].strip()
				await replace_pins(message.channel, functools.partial(bump_time_message.send, message.channel, argument))


	async def reaction_changed(payload: discord.RawReactionActionEvent, added: bool):
		if payload.user_id == client.user.id:
			return
		
		channel = client.get_channel(payload.channel_id)
		if channel.name != config.get_channel_name():
			return
		
		message = await message_cache.get_message(payload.message_id, channel)	
		if message:
			member = channel.guild.get_member(payload.user_id)
			if added:
				found_reactions_cache.add_found_reaction(payload.message_id, payload.emoji, member)
			else:
				found_reactions_cache.remove_found_reaction(payload.message_id, payload.emoji, member)
			
			if bump_message.handles(message):
				await bump_message.update(message)
			elif bump_time_message.handles(message):
				await bump_time_message.update(message)

	@client.event
	async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
		await reaction_changed(payload, True)

	@client.event
	async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
		await reaction_changed(payload, False)

	discord_client.run_client()
	return 0

if __name__ == '__main__':
	sys.exit(main())