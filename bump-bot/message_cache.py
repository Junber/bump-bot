from typing import Dict
import discord

message_cache: Dict[int, discord.Message] = {}

async def get_message(message_id: int, channel: discord.TextChannel) -> discord.Message | None:
	if message_id in message_cache:
		return message_cache[message_id]

	async for message in channel.history():
		if message.id == message_id:
			message_cache[message_id] = message
			return message
	
	return None