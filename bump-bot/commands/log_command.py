from typing import override
import discord

from commands.command import BasicCommand
import bump_bot_config as config


class LogCommand(BasicCommand):
    @override
    def get_config(self) -> config.BasicCommandConfig:
        return config.get_log()

    @override
    async def on_message(self, message: discord.Message, channel: discord.TextChannel) -> None:
        await channel.send(
            self.get_message_content(),
            file=discord.File(config.get_log_file_name()),
        )
