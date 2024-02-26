import datetime
from typing import Tuple
import discord

import bump_bot_config as config
from calendar_client import calendar
import discord_client
import found_reactions_cache
from utils import find_closest_index
from commands.voting_command import VotingCommand


WEEKDAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def find_date(weekday: str, message_date: datetime.date) -> datetime.date:
    weekday_index = find_closest_index(WEEKDAYS, weekday.lower())
    date = message_date + datetime.timedelta(weekday_index - message_date.weekday())
    if weekday_index < message_date.weekday():
        date += datetime.timedelta(7)
    return date


class BumpTimeCommand(VotingCommand):
    @staticmethod
    def get_embed_and_time(
        found_reactions: found_reactions_cache.FoundReactions, date: datetime.date
    ) -> Tuple[discord.Embed, datetime.time | None]:
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

        found_members: set[discord.Member] = set()
        message_text_options_chunk = ""
        earliest_possible_time = ""
        for reaction in config.get_bump_time_reactions():
            members = set()
            if reaction in found_reactions:
                members |= found_reactions[reaction]
            members -= found_members

            if len(members) > 0:
                found_members |= members
                if len(found_members) == len(members_who_voted):
                    earliest_possible_time = config.get_bump_time_reactions()[reaction]
                    message_text += "**Earliest possible time: {}**\n\n".format(
                        earliest_possible_time
                    )

            message_text_options_chunk += " {} ({}): ".format(
                config.get_bump_time_reactions()[reaction],
                discord_client.get_emoji(reaction),
            )

            message_text_options_chunk += VotingCommand.member_list(members, members_who_voted, "-")
            message_text_options_chunk += "\n"

        message_text += message_text_options_chunk
        embed = discord.Embed(title=config.get_bump_time_embed_title().format()).add_field(
            name=config.get_bump_time_embed_field_name(), value=message_text
        )

        earliest_datetime = None
        if len(members_who_voted) >= config.get_required_votes():
            earliest_datetime = datetime.time.fromisoformat(earliest_possible_time)

        return (embed, earliest_datetime)

    # @override
    def handles_message(self, message: discord.Message, channel: discord.TextChannel) -> bool:
        return (
            channel.name == config.get_voting_channel_name()
            and message.content != config.get_voting_trigger()
            and message.content.startswith(config.get_voting_trigger())
        )

    # @override
    async def send_poll(
        self, message: discord.Message, channel: discord.TextChannel
    ) -> discord.Message:
        argument = message.content[len(config.get_voting_trigger()) :].strip()
        content = (
            config.get_bump_time_message_content_prefix()
            + argument
            + config.get_bump_time_message_content_postfix()
        )
        date = find_date(argument, datetime.date.today())
        (embed, _) = self.get_embed_and_time({}, date)
        poll_message: discord.Message = await channel.send(content, embed=embed)
        await found_reactions_cache.initialize_empty_reactions(poll_message.id)
        for reaction in config.get_bump_time_reactions():
            emoji = discord_client.get_emoji(reaction)
            if emoji is not None:
                await poll_message.add_reaction(emoji)  # Await here because order is important

        calendar.create_event(date, None)

        return poll_message

    # @override
    def handles_reactions_in_channel(
        self, channel: discord.TextChannel, emoji: discord.PartialEmoji
    ) -> bool:
        return channel.name == config.get_voting_channel_name()

    # @override
    def handles_reactions(self, message: discord.Message) -> bool:
        return (
            message.content.startswith(config.get_bump_time_message_content_prefix())
            and message.content.endswith(config.get_bump_time_message_content_postfix())
            and message.author == discord_client.get_client().user
        )

    # @override
    async def on_reaction_changed(self, message: discord.Message, reaction_added: bool) -> None:
        if not await self.update_message_wait.wait():
            return

        argument = message.content[
            len(config.get_bump_time_message_content_prefix()) : -len(
                config.get_bump_time_message_content_postfix()
            )
        ]
        reactions = await found_reactions_cache.get_found_reactions(message)
        date = find_date(argument, message.created_at.date())

        if len(reactions[config.get_voting_cancel_reaction()]):
            await message.edit(content="This poll was canceled", embed=None)
            calendar.delete_events(date)
            return

        (embed, time) = self.get_embed_and_time(reactions, date)
        await message.edit(embed=embed)

        if time and calendar.create_event(date, time):
            await message.channel.send("New time found: " + time.strftime("%H:%M"))
