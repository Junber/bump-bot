import os
import sys
from typing import Type
import discord

import discord_client
from commands import *
from commands.command import Command, ReactionsCommand
import message_cache
import found_reactions_cache


def add_commands(
    superclass: Type, commands: list[Command], reactions_commands: list[ReactionsCommand]
):
    for command_class in superclass.__subclasses__():
        if len(command_class.__subclasses__()):
            add_commands(command_class, commands, reactions_commands)
            continue
        command = command_class()
        commands.append(command)
        if isinstance(command, ReactionsCommand):
            reactions_commands.append(command)


def main() -> int:
    client = discord_client.get_client()

    commands: list[Command] = []
    reactions_commands: list[ReactionsCommand] = []
    add_commands(Command, commands, reactions_commands)

    @client.event  # type: ignore
    async def on_message(message: discord.Message) -> None:
        if message.author == client.user:
            return

        if not isinstance(message.channel, discord.TextChannel):
            return

        for command in commands:
            if command.handles_message(message, message.channel):
                await command.on_message(message, message.channel)

    async def reaction_changed(payload: discord.RawReactionActionEvent, added: bool) -> None:
        channel = client.get_channel(payload.channel_id)
        if not isinstance(channel, discord.TextChannel) or not any(
            [
                command.handles_reactions_in_channel(channel, payload.emoji)
                for command in reactions_commands
            ]
        ):
            return

        member = channel.guild.get_member(payload.user_id)
        if member is None:
            return

        if added:
            await found_reactions_cache.add_found_reaction(
                payload.message_id, payload.emoji, member
            )
        else:
            await found_reactions_cache.remove_found_reaction(
                payload.message_id, payload.emoji, member
            )

        if client.user is None or payload.user_id == client.user.id:
            return

        message = await message_cache.get_message(payload.message_id, channel)
        if not message:
            return

        for command in reactions_commands:
            if command.handles_reactions_in_channel(
                channel, payload.emoji
            ) and command.handles_reactions(message):
                await command.on_reaction_changed(message, added)

    @client.event
    async def on_raw_reaction_add(payload: discord.RawReactionActionEvent) -> None:
        await reaction_changed(payload, True)

    @client.event
    async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent) -> None:
        await reaction_changed(payload, False)

    @client.event
    async def on_raw_message_edit(payload: discord.RawMessageUpdateEvent) -> None:
        message_cache.remove_message(payload.message_id)

    discord_client.run_client()
    return 0


if __name__ == "__main__":
    sys.exit(main())
