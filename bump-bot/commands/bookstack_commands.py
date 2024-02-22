from abc import abstractmethod
from typing import override
import discord

from commands.command import BasicCommand, ReactionsCommand
import bump_bot_config as config
import bookstack_export


class BookstackReactionsCommand(ReactionsCommand):
    @override
    def handles_message(self, message: discord.Message, channel: discord.TextChannel) -> bool:
        return False

    @override
    async def on_message(self, message: discord.Message, channel: discord.TextChannel) -> None:
        pass

    @override
    def handles_reactions_in_channel(
        self, channel: discord.TextChannel, emoji: discord.PartialEmoji
    ) -> bool:
        return (
            channel.name == config.get_bookstack_channel_name()
            and emoji.name == config.get_bookstack_trigger()
        )

    @override
    def handles_reactions(self, message: discord.Message) -> bool:
        return True

    @override
    async def on_reaction_changed(self, message: discord.Message, reaction_added: bool) -> None:
        if reaction_added:
            await bookstack_export.export_if_needed(message)
        else:
            await bookstack_export.unexport_if_needed(message)


class BasicBookstackCommand(BasicCommand):
    @abstractmethod
    async def perform_action(self, bookstack_channel: discord.TextChannel) -> None:
        pass

    @override
    async def on_message(self, message: discord.Message, channel: discord.TextChannel) -> None:
        bookstack_channel = discord.utils.get(
            channel.guild.channels,
            name=config.get_bookstack_channel_name(),
        )
        if not isinstance(bookstack_channel, discord.TextChannel):
            return
        await self.perform_action(bookstack_channel)
        await message.channel.send(self.get_message_content())


class BookstackExportAllCommand(BasicBookstackCommand):
    @override
    def get_config(self) -> config.BasicCommandConfig:
        return config.get_bookstack_export_all()

    @override
    async def perform_action(self, bookstack_channel: discord.TextChannel) -> None:
        await bookstack_export.export_all(bookstack_channel)


class BookstackUnexportAllCommand(BasicBookstackCommand):
    @override
    def get_config(self) -> config.BasicCommandConfig:
        return config.get_bookstack_unexport_all()

    @override
    async def perform_action(self, bookstack_channel: discord.TextChannel) -> None:
        await bookstack_export.unexport_all(bookstack_channel)


class BookstackClearEmojiCommand(BasicBookstackCommand):
    @override
    def get_config(self) -> config.BasicCommandConfig:
        return config.get_bookstack_clear_emoji()

    @override
    async def perform_action(self, bookstack_channel: discord.TextChannel) -> None:
        await bookstack_export.clear_emoji(bookstack_channel)
