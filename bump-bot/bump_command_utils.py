import discord

import bump_bot_config as config


def get_week_offset(message: discord.Message) -> int:
    if message.content.lower() == config.get_voting_trigger():
        return 1
    parts = message.content.lower().strip().split()
    if len(parts) != 2 or parts[0] != config.get_voting_trigger() or not parts[1].isnumeric():
        return -1

    return int(parts[1])


def bump_command_handles_message(message: discord.Message, channel: discord.TextChannel) -> bool:
    return channel.name == config.get_voting_channel_name() and get_week_offset(message) >= 0
