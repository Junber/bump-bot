from typing import override
import discord

import bump_bot_config as config
from commands.voting_command import VotingCommand
import discord_client
import found_reactions_cache


class BumpCommand(VotingCommand):
    @staticmethod
    def get_embed(found_reactions: found_reactions_cache.FoundReactions) -> discord.Embed:
        members_who_voted = set()
        for reaction in found_reactions:
            members_who_voted |= found_reactions[reaction]

        message_text = "Current Voters: "

        if len(members_who_voted) == 0:
            message_text += "No votes yet"
        else:
            member: discord.Member
            for member in sorted(members_who_voted, key=lambda x: x.display_name):
                message_text += member.display_name
                message_text += ", "
            message_text = message_text.removesuffix(", ")

        message_text += " "

        if len(members_who_voted) >= config.get_required_votes():
            message_text += ":white_check_mark:"
        else:
            message_text += ":x:"

        message_text += "\n"

        for reaction in config.get_bump_reactions():
            members = set()
            if reaction in found_reactions:
                members = found_reactions[reaction]

            if len(members) == len(members_who_voted):
                message_text += ":white_check_mark:"
            else:
                message_text += ":x:"

            message_text += " {} ({}): ".format(
                config.get_bump_reactions()[reaction], discord_client.get_emoji(reaction)
            )

            message_text += VotingCommand.member_list(members, members_who_voted, "No one")
            message_text += "\n"

        return discord.Embed(title=config.get_bump_embed_title()).add_field(
            name=config.get_bump_embed_field_name(), value=message_text
        )

    @override
    def handles_message(self, message: discord.Message, channel: discord.TextChannel) -> bool:
        return (
            channel.name == config.get_voting_channel_name()
            and message.content == config.get_voting_trigger()
        )

    @override
    async def send_poll(
        self, message: discord.Message, channel: discord.TextChannel
    ) -> discord.Message:
        poll_message: discord.Message = await channel.send(
            config.get_bump_message_content(), embed=self.get_embed({})
        )
        await found_reactions_cache.initialize_empty_reactions(poll_message.id)
        for reaction in config.get_bump_reactions():
            emoji = discord_client.get_emoji(reaction)
            if emoji is not None:
                await poll_message.add_reaction(emoji)  # Await here because order is important
        return poll_message

    @override
    def handles_reactions_in_channel(
        self, channel: discord.TextChannel, emoji: discord.PartialEmoji
    ) -> bool:
        return channel.name == config.get_voting_channel_name()

    @override
    def handles_reactions(self, message: discord.Message) -> bool:
        return (
            bool(message.content == config.get_bump_message_content())
            and message.author == discord_client.get_client().user
        )

    @override
    async def on_reaction_changed(self, message: discord.Message, reaction_added: bool) -> None:
        if not await self.update_message_wait.wait():
            return

        await message.edit(
            embed=self.get_embed(await found_reactions_cache.get_found_reactions(message))
        )
