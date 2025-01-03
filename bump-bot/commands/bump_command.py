import asyncio
from calendar import TextCalendar
import datetime
from typing import Tuple
import discord

from cancelable_wait import CancelableWait
import bump_bot_config as config
from commands.voting_command import VotingCommand
from commands.bump_time_command import BumpTimeCommand
import discord_client
import found_reactions_cache


class SelectDayView(discord.ui.View):
    def __init__(self, possible_days: list[str]) -> None:
        super().__init__(timeout=None)
        for day in possible_days:
            self.add_button(day)

    def add_button(self, day: str) -> None:
        button = discord.ui.Button(label=day)

        async def callback(interaction: discord.Interaction) -> None:
            if not isinstance(interaction.channel, discord.TextChannel):
                return
            await interaction.response.send_message(BumpTimeCommand.get_start_poll_command(day))
            message = await interaction.original_response()
            if not message:
                return
            await BumpTimeCommand.start_time_poll(message, interaction.channel)

        button.callback = callback
        self.add_item(button)


class BumpCommand(VotingCommand):
    announce_results_wait = CancelableWait(30.0)
    last_time_poll_started: datetime.datetime | None = None
    last_result: list[str] | None = None

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
        if len(members_who_voted) >= config.get_required_votes() or len(possible_days) == 0:
            result = possible_days

        return (
            discord.Embed(title=config.get_bump_embed_title()).add_field(
                name=config.get_bump_embed_field_name(), value=message_text
            ),
            result,
        )

    # @override
    async def handles_message(self, message: discord.Message, channel: discord.TextChannel) -> bool:
        if channel.name != config.get_voting_channel_name():
            return False

        if BumpTimeCommand.handles_message_static(message, channel):
            await self.announce_results_wait.cancel()
            self.last_time_poll_started = message.created_at
        return message.content.lower() == config.get_voting_trigger()

    # @override
    async def send_poll(self, message: discord.Message) -> discord.Message:
        (embed, _) = self.get_embed_and_result({})
        poll_message = await message.reply(config.get_bump_message_content(), embed=embed)
        await found_reactions_cache.initialize_empty_reactions(poll_message.id)
        for reaction in config.get_bump_reactions():
            emoji = discord_client.get_emoji(reaction)
            if emoji is not None:
                await poll_message.add_reaction(emoji)  # Await here because order is important
        return poll_message

    # @override
    def handles_reactions_in_channel(
        self, channel: discord.TextChannel, emoji: discord.PartialEmoji
    ) -> bool:
        return channel.name == config.get_voting_channel_name()

    # @override
    def handles_reactions(self, message: discord.Message) -> bool:
        return (
            bool(message.content == config.get_bump_message_content())
            and message.author == discord_client.get_client().user
        )

    async def announce_results(self, result: list[str], message: discord.Message) -> None:
        if not await self.announce_results_wait.wait() or not isinstance(
            message.channel, discord.TextChannel
        ):
            return

        if len(result) == 0:
            await message.reply(
                "It seems like no date could be found, sorry. Better luck next time."
            )
        elif len(result) == 1:
            one_day_message = await message.reply("Only one date works, so we'll use that.")
            await BumpTimeCommand.start_time_poll(
                await one_day_message.reply(BumpTimeCommand.get_start_poll_command(result[0])),
                message.channel,
            )
        else:
            await message.reply(
                "Multiple days ({}) work. Sort that one out yourselves.".format(", ".join(result)),
                view=SelectDayView(result),
            )

    # @override
    async def on_reaction_changed(self, message: discord.Message, reaction_added: bool) -> None:
        if not await self.update_message_wait.wait():
            return

        reactions = await found_reactions_cache.get_found_reactions(message)

        if config.get_voting_cancel_reaction() in reactions and len(
            reactions[config.get_voting_cancel_reaction()]
        ):
            await message.edit(content="This poll was canceled", embed=None)
            return

        (embed, result) = self.get_embed_and_result(reactions)
        await message.edit(embed=embed)

        if (
            result is not None
            and result != self.last_result
            and (
                not self.last_time_poll_started or self.last_time_poll_started < message.created_at
            )
        ):
            asyncio.create_task(self.announce_results(result, message))
        self.last_result = result
