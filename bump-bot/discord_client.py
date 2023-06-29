import discord

client = None

def get_client():
	global client
	if not client:
		intents = discord.Intents.default()
		intents.message_content = True
		intents.members = True
		client = discord.Client(intents=intents)
		
	return client