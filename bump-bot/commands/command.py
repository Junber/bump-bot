from abc import ABC, abstractmethod
import discord

import bump_bot_config as config


class Command(ABC):
    @abstractmethod
    def handles_message(self, message: discord.Message, channel: discord.TextChannel) -> bool:
        pass

    @abstractmethod
    async def on_message(self, message: discord.Message, channel: discord.TextChannel) -> None:
        pass


class BasicCommand(Command):
    @abstractmethod
    def get_config(self) -> config.BasicCommandConfig:
        pass

    def get_message_content(self) -> str:
        return self.get_config().get_message_content()

    # @override
    def handles_message(self, message: discord.Message, channel: discord.TextChannel) -> bool:
        command_config = self.get_config()
        return (
            channel.name == command_config.get_channel_name()
            and message.content == command_config.get_trigger()
        )


class ReactionsCommand(Command):
    @abstractmethod
    def handles_reactions_in_channel(
        self, channel: discord.TextChannel, emoji: discord.PartialEmoji
    ) -> bool:
        pass

    @abstractmethod
    def handles_reactions(self, message: discord.Message) -> bool:
        pass

    @abstractmethod
    async def on_reaction_changed(self, message: discord.Message, reaction_added: bool) -> None:
        pass
