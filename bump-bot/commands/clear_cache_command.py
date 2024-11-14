import discord

from commands.command import BasicCommand
import bump_bot_config as config
import found_reactions_cache
import message_cache


class ClearCacheCommand(BasicCommand):
    # @override
    def get_config(self) -> config.BasicCommandConfig:
        return config.get_clear_cache()

    # @override
    async def on_message(self, message: discord.Message, channel: discord.TextChannel) -> None:
        await found_reactions_cache.clear_cache()
        message_cache.clear_cache()
