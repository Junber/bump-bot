import asyncio
from typing import Tuple, override
import discord

from cancelable_wait import CancelableWait
import bump_bot_config as config
from commands.voting_command import VotingCommand
from commands.bump_time_command import BumpTimeCommand
import discord_client
import found_reactions_cache


class BumpCommand(VotingCommand):
    announce_results_wait = CancelableWait(300.0)

    @staticmethod
    def get_embed_and_result(
        found_reactions: found_reactions_cache.FoundReactions,
    ) -> Tuple[discord.Embed, list[str] | None]:
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

        possible_days: list[str] = []
        for reaction in config.get_bump_reactions():
            members = set()
            if reaction in found_reactions:
                members = found_reactions[reaction]

            day_name = config.get_bump_reactions()[reaction]

            if len(members) == len(members_who_voted):
                message_text += ":white_check_mark:"
                possible_days.append(day_name)
            else:
                message_text += ":x:"

            message_text += " {} ({}): ".format(day_name, discord_client.get_emoji(reaction))

            message_text += VotingCommand.member_list(members, members_who_voted, "No one")
            message_text += "\n"

        result = None
        if len(members_who_voted) >= config.get_required_votes():
            result = possible_days

        return (
            discord.Embed(title=config.get_bump_embed_title()).add_field(
                name=config.get_bump_embed_field_name(), value=message_text
            ),
            result,
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
        (embed, _) = self.get_embed_and_result({})
        poll_message: discord.Message = await channel.send(
            config.get_bump_message_content(), embed=embed
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

    async def announce_results(self, result: list[str], channel: discord.TextChannel) -> None:
        if not await self.announce_results_wait.wait():
            return

        if len(result) == 0:
            await channel.send(
                "It seems like no date could be found, sorry. Better luck next time."
            )
        elif len(result) == 1:
            await channel.send("Only one date works, so we'll use that.")
            bump_time_message = await channel.send(config.get_voting_trigger() + " " + result[0])

            # TODO: avoid creating new instance here
            await BumpTimeCommand().on_message(bump_time_message, channel)
        else:
            await channel.send("Multiple days work. Sort that one out yourselves.")

    @override
    async def on_reaction_changed(self, message: discord.Message, reaction_added: bool) -> None:
        if not await self.update_message_wait.wait():
            return

        (embed, result) = self.get_embed_and_result(
            await found_reactions_cache.get_found_reactions(message)
        )

        await message.edit(embed=embed)

        if result is not None and isinstance(message.channel, discord.TextChannel):
            asyncio.create_task(self.announce_results(result, message.channel))
