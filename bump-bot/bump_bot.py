import asyncio
import functools
import sys
from typing import Any, Callable, Coroutine
import discord

import bump_bot_config as config
import discord_client
import message_cache
import found_reactions_cache
import bump_message
import bump_time_message
from bookstack_client import bookstack
import bookstack_export


def main() -> int:
    client = discord_client.get_client()

    async def replace_pins(
        channel: discord.TextChannel,
        new_pin_function: Callable[[], Coroutine[Any, Any, discord.Message]],
    ) -> None:
        async with asyncio.TaskGroup() as tg:
            for pinned in await channel.pins():  # TODO: Cache pins?
                tg.create_task(pinned.unpin())
            new_message = await new_pin_function()
            tg.create_task(new_message.pin())

    @client.event  # type: ignore
    async def on_message(message: discord.Message) -> None:
        if message.author == client.user:
            return

        if not isinstance(message.channel, discord.TextChannel):
            return

        if message.channel.name == config.get_voting_channel_name():
            if message.content == config.get_voting_trigger():
                await replace_pins(
                    message.channel,
                    functools.partial(bump_message.send, message.channel),
                )
            elif message.content.startswith(config.get_voting_trigger()):
                argument = message.content[len(config.get_voting_trigger()) :].strip()
                await replace_pins(
                    message.channel,
                    functools.partial(bump_time_message.send, message.channel, argument),
                )

        if message.channel.name == config.get_shutdown().get_channel_name():
            if message.content == config.get_shutdown().get_trigger():
                await message.channel.send(config.get_shutdown().get_message_content())
                await client.close()

        if message.channel.name == config.get_log().get_channel_name():
            if message.content == config.get_log().get_trigger():
                await message.channel.send(
                    config.get_log().get_message_content(),
                    file=discord.File(config.get_log_file_name()),
                )

        if message.channel.name == config.get_bookstack_export_all().get_channel_name():
            if message.content == config.get_bookstack_export_all().get_trigger():
                channel = discord.utils.get(
                    message.channel.guild.channels,
                    name=config.get_bookstack_channel_name(),
                )
                if not isinstance(channel, discord.TextChannel):
                    return
                await bookstack_export.export_all(channel)
                await message.channel.send(config.get_bookstack_export_all().get_message_content())

        if message.channel.name == config.get_bookstack_unexport_all().get_channel_name():
            if message.content == config.get_bookstack_unexport_all().get_trigger():
                channel = discord.utils.get(
                    message.channel.guild.channels,
                    name=config.get_bookstack_channel_name(),
                )
                if not isinstance(channel, discord.TextChannel):
                    return
                await bookstack_export.unexport_all(channel)
                await message.channel.send(
                    config.get_bookstack_unexport_all().get_message_content()
                )

        if message.channel.name == config.get_bookstack_clear_emoji().get_channel_name():
            if message.content == config.get_bookstack_clear_emoji().get_trigger():
                channel = discord.utils.get(
                    message.channel.guild.channels,
                    name=config.get_bookstack_channel_name(),
                )
                if not isinstance(channel, discord.TextChannel):
                    return
                await bookstack_export.clear_emoji(channel)
                await message.channel.send(config.get_bookstack_clear_emoji().get_message_content())

    async def reaction_changed(payload: discord.RawReactionActionEvent, added: bool) -> None:
        channel = client.get_channel(payload.channel_id)
        if not isinstance(channel, discord.TextChannel):
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

        if not (
            channel.name == config.get_voting_channel_name()
            or (
                channel.name == config.get_bookstack_channel_name()
                and payload.emoji.name == config.get_bookstack_trigger()
            )
        ):
            return

        message = await message_cache.get_message(payload.message_id, channel)
        if not message:
            return

        if channel.name == config.get_voting_channel_name():
            if bump_message.handles(message):
                await bump_message.update(message)
            elif bump_time_message.handles(message):
                await bump_time_message.update(message)

        elif (
            channel.name == config.get_bookstack_channel_name()
            and payload.emoji.name == config.get_bookstack_trigger()
        ):
            if added:
                await bookstack_export.export_if_needed(message)
            else:
                await bookstack_export.unexport_if_needed(message)

    @client.event  # type: ignore
    async def on_raw_reaction_add(payload: discord.RawReactionActionEvent) -> None:
        await reaction_changed(payload, True)

    @client.event  # type: ignore
    async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent) -> None:
        await reaction_changed(payload, False)

    @client.event  # type: ignore
    async def on_raw_message_edit(payload: discord.RawMessageUpdateEvent) -> None:
        message_cache.remove_message(payload.message_id)

    discord_client.run_client()
    return 0


if __name__ == "__main__":
    sys.exit(main())
