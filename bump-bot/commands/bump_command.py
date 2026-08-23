import asyncio
import datetime
from typing import Tuple
import discord

import bump_bot_config as config
from commands.voting_command import VotingCommand
from commands.bump_time_command import BumpTimeCommand
import discord_client
import found_reactions_cache
import message_cache
from bump_command_utils import *


class SelectDayView(discord.ui.View):
    def __init__(self, possible_days: list[str], week_start: datetime.date) -> None:
        super().__init__(timeout=None)
        self.week_start = week_start
        for day in possible_days:
            self.add_button(day)

    def add_button(self, day: str) -> None:
        button = discord.ui.Button(label=day)

        async def callback(interaction: discord.Interaction) -> None:
            if not isinstance(interaction.channel, discord.TextChannel):
                return
            await interaction.response.send_message(
                BumpTimeCommand.get_start_poll_command(day, self.week_start)
            )
            message = await interaction.original_response()
            if not message:
                return
            await BumpTimeCommand.start_time_poll(message, interaction.channel)

        button.callback = callback
        self.add_item(button)


def get_week_start(message: discord.Message) -> datetime.date:
    week_offset = get_week_offset(message)
    date = message.created_at.date()
    return date + datetime.timedelta(days=7 * week_offset - date.weekday())


class BumpCommand(VotingCommand):
    last_time_poll_started: datetime.datetime | None = None
    last_result: dict[discord.Message, list[str]] = {}
    last_date_poll_week_start: datetime.date | None = None

    @staticmethod
    def get_embed_and_result(
        found_reactions: found_reactions_cache.FoundReactions, week_start: datetime.date
    ) -> Tuple[discord.Embed, list[str] | None]:
        members_who_voted = set()
        for reaction in found_reactions:
            if reaction in config.get_bump_reactions():
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

        one_day = datetime.timedelta(days=1)

        date = week_start
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

            message_text += f" **{day_name}** ({date.strftime(config.get_date_format())}) ({discord_client.get_emoji(reaction)}): "

            message_text += VotingCommand.member_list(members, members_who_voted, "No one")
            message_text += "\n"
            date += one_day

        result = None
        if len(members_who_voted) >= config.get_required_votes() or len(possible_days) == 0:
            result = possible_days

        return (
            discord.Embed(
                title=f"{config.get_bump_embed_title()} ({week_start.strftime(config.get_date_format())} - {(date - one_day).strftime(config.get_date_format())})"
            ).add_field(name=config.get_bump_embed_field_name(), value=message_text),
            result,
        )

    # @override
    async def handles_message(self, message: discord.Message, channel: discord.TextChannel) -> bool:
        if BumpTimeCommand.handles_message_static(message, channel):
            await self.announce_result_wait.cancel()
            self.last_time_poll_started = message.created_at
        return bump_command_handles_message(message, channel)

    async def send_clarifying_poll_message(self, message: discord.Message) -> discord.Message:
        week_offset = -1
        explanation = ""
        if self.last_date_poll_week_start == None:
            explanation = "No date for last poll recorded."
        else:
            week_since_last_poll = (
                message.created_at.date() - self.last_date_poll_week_start
            ).days // 7
            if week_since_last_poll >= 2:
                explanation = "The last recorded poll was for a week before last."
            elif week_since_last_poll == 1:
                explanation = (
                    "The last recorded poll was for last week. So, we'll use the current week."
                )
                week_offset = 0
            elif week_since_last_poll == 0:
                explanation = "The last recorded poll was already for the current week. So, we'll use the next week."
                week_offset = 1
            else:
                explanation = "The last recorded poll was already for a future week. So, we'll use the week after that one."
                week_offset = 1 - week_since_last_poll

        if week_offset < 0:
            WEEKDAY_CUTOFF = 2
            explanation += " Using weekday logic: "
            if message.created_at.date().weekday() <= WEEKDAY_CUTOFF:
                explanation += f"Since it's not yet {WEEKDAYS[WEEKDAY_CUTOFF + 1].capitalize()}, we'll use the current week."
                week_offset = 0
            else:
                explanation += f"Since it's already past {WEEKDAYS[WEEKDAY_CUTOFF].capitalize()}, we'll use the next week."
                week_offset = 1

        await message.channel.send(explanation)
        return await message.channel.send(config.get_voting_trigger() + " " + str(week_offset))

    # @override
    async def send_poll(self, message: discord.Message) -> discord.Message:
        if message.content.lower() == config.get_voting_trigger():
            return await self.send_poll(await self.send_clarifying_poll_message(message))

        self.last_date_poll_week_start = get_week_start(message)
        embed, _ = self.get_embed_and_result({}, self.last_date_poll_week_start)
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
            message.author == discord_client.get_client().user
            and message.content == config.get_bump_message_content()
        )

    async def announce_results(
        self, result: list[str], message: discord.Message, original_message: discord.Message
    ) -> None:
        if not await self.announce_result_wait.wait():
            return

        if not isinstance(message.channel, discord.TextChannel):
            raise

        if len(result) == 0:
            await message.reply(
                "It seems like no date could be found, sorry. Better luck next time."
            )
        elif len(result) == 1:
            await message.reply("Only one date works, so we'll use that.")
            await BumpTimeCommand.start_time_poll(
                await message.channel.send(
                    BumpTimeCommand.get_start_poll_command(
                        result[0], get_week_start(original_message)
                    )
                ),
                message.channel,
            )
        else:
            await message.reply(
                f"Multiple days ({", ".join(result)}) work. Sort that one out yourselves.",
                view=SelectDayView(result, get_week_start(original_message)),
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

        original_message = await message_cache.get_replied(message)

        embed, result = self.get_embed_and_result(
            reactions,
            get_week_start(original_message),
        )
        await message.edit(embed=embed)

        if result is None:
            await self.announce_result_wait.cancel()
        elif result != self.last_result.get(message, None) and (
            not self.last_time_poll_started or self.last_time_poll_started < message.created_at
        ):
            self.last_result[message] = result
            asyncio.create_task(self.announce_results(result, message, original_message))
