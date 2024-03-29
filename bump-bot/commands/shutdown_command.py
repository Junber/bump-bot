import discord

from commands.command import BasicCommand
import bump_bot_config as config
import discord_client


class ShutdownCommand(BasicCommand):
    # @override
    def get_config(self) -> config.BasicCommandConfig:
        return config.get_shutdown()

    # @override
    async def on_message(self, message: discord.Message, channel: discord.TextChannel) -> None:
        await channel.send(self.get_message_content())
        await discord_client.get_client().close()
