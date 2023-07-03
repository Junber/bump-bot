import asyncio
import discord

import config
import discord_client
import message_cache
import found_reactions_cache
import bump_message

config.load_config()
client = discord_client.get_client()

reaction_counts = {}

@client.event
async def on_message(message: discord.Message):
	if message.author == client.user:
		return

	if message.content == config.get_trigger():
		async with asyncio.TaskGroup() as tg:
			for pinned in await message.channel.pins(): # TODO: Cache pins?
				tg.create_task(pinned.unpin())
			new_message = await bump_message.send_bump_message(message.channel)
			tg.create_task(new_message.pin())

async def reaction_changed(payload: discord.RawReactionActionEvent, added: bool):
	if payload.user_id == client.user.id:
		return
	
	channel = client.get_channel(payload.channel_id)
	if channel.name != config.get_channel_name():
		return
	
	message = await message_cache.get_message(payload.message_id, channel)	
	if message:

		# reaction_removed events do not have a member included while reaction_added ones do.
		member = channel.guild.get_member(payload.user_id)
		if added:
			found_reactions_cache.add_found_reaction(payload.message_id, payload.emoji, member)
		else:
			found_reactions_cache.remove_found_reaction(payload.message_id, payload.emoji, member)
		await bump_message.update_bump_message(message)

@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
	await reaction_changed(payload, True)

@client.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
	await reaction_changed(payload, False)

client.run(config.get_token())
