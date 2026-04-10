import asyncio
import datetime
from typing import Tuple
import discord

import bump_bot_config as config
from calendar_client import get_calendar
import discord_client
import found_reactions_cache
from utils import find_closest_index
from commands.voting_command import VotingCommand
import message_cache
from bump_command_utils import bump_command_handles_message


WEEKDAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def find_date(weekday_index: int, message_date: datetime.date, week_offset: int) -> datetime.date:
    return message_date + datetime.timedelta(
        days=weekday_index - message_date.weekday() + 7 * week_offset
    )


def find_weekday_index(argument: str) -> int:
    return find_closest_index(WEEKDAYS, argument.lower(), config.get_max_edit_distance())


def get_argument(message: discord.Message) -> str:
    parts = message.content.strip().split()
    return parts[1]


def get_default_offset(weekday_index: int, message_date: datetime.date) -> int:
    return 1 if weekday_index < message_date.weekday() else 0


def get_week_offset(message: discord.Message, weekday_index: int) -> int:
    parts = message.content.lower().strip().split()
    if parts[0] != config.get_voting_trigger():
        return -1
    if len(parts) == 2:
        return get_default_offset(weekday_index, message.created_at)

    if len(parts) != 3 or not parts[2].isnumeric():
        return -1

    return int(parts[2])


def find_date_and_in_person(message: discord.Message) -> tuple[datetime.date, bool]:
    weekday_index = find_weekday_index(get_argument(message))
    in_person = WEEKDAYS[weekday_index] in config.get_bump_time_in_person_days()
    date = find_date(
        weekday_index, message.created_at.date(), get_week_offset(message, weekday_index)
    )
    return (date, in_person)


def get_week_start(message: discord.Message) -> datetime.date:
    weekday_index = find_weekday_index(get_argument(message))
    week_offset = get_week_offset(message, weekday_index)
    date = message.created_at.date()
    return date - datetime.timedelta(days=date.weekday() + 7 * week_offset)


class BumpTimeCommand(VotingCommand):
    last_result: Tuple[datetime.time, bool] | None = None

    @staticmethod
    def get_embed_and_time(
        found_reactions: found_reactions_cache.FoundReactions, date: datetime.date, in_person: bool
    ) -> Tuple[discord.Embed, datetime.time | None, bool]:
        members_who_voted = set()
        for reaction in found_reactions:
            if reaction in config.get_bump_time_reactions():
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

        in_person_happening = False
        if in_person:
            reaction = config.get_bump_time_in_person_reaction()
            members = found_reactions.get(reaction, set())
            message_text += "\nIn-person ({} to opt-out): ".format(
                discord_client.get_emoji(reaction)
            )
            if len(members):
                message_text += ":x: " + VotingCommand.raw_member_list(members)
            elif len(members_who_voted) < config.get_required_votes():
                message_text += ":white_check_mark: As yet possible"
            else:
                message_text += ":white_check_mark: Yes!"
                in_person_happening = True

        embed = discord.Embed(
            title="{} ({})".format(
                config.get_bump_time_embed_title(), date.strftime(config.get_date_format())
            )
        ).add_field(name=config.get_bump_time_embed_field_name(), value=message_text)

        earliest_datetime = None
        if len(members_who_voted) >= config.get_required_votes():
            earliest_datetime = datetime.time.fromisoformat(earliest_possible_time)

        return (embed, earliest_datetime, in_person_happening)

    @staticmethod
    def get_start_poll_command(day: str, week_offset: int) -> str:
        result = config.get_voting_trigger() + " " + day
        if get_default_offset(find_weekday_index(day), datetime.date.today()) != week_offset:
            result += " " + str(week_offset)
        return result

    @staticmethod
    async def start_time_poll(message: discord.Message, channel: discord.TextChannel) -> None:
        # TODO: avoid creating new instance here
        await BumpTimeCommand().on_message(message, channel)

    @staticmethod
    def handles_message_static(message: discord.Message, channel: discord.TextChannel) -> bool:
        if channel.name != config.get_voting_channel_name() or bump_command_handles_message(
            message, channel
        ):
            return False

        weekday_index = find_weekday_index(get_argument(message))
        if weekday_index <= 0:
            return False
        return get_week_offset(message, weekday_index) >= 0

    # @override
    async def handles_message(self, message: discord.Message, channel: discord.TextChannel) -> bool:
        return self.handles_message_static(message, channel)

    # @override
    async def send_poll(self, message: discord.Message) -> discord.Message:
        content = (
            config.get_bump_time_message_content_prefix()
            + get_argument(message)
            + config.get_bump_time_message_content_postfix()
        )
        (date, in_person) = find_date_and_in_person(message)
        (embed, _, _) = self.get_embed_and_time({}, date, in_person)
        poll_message: discord.Message = await message.reply(content, embed=embed)
        await found_reactions_cache.initialize_empty_reactions(poll_message.id)
        for reaction in config.get_bump_time_reactions():
            emoji = discord_client.get_emoji(reaction)
            if emoji is not None:
                await poll_message.add_reaction(emoji)  # Await here because order is important

        if in_person:
            emoji = discord_client.get_emoji(config.get_bump_time_in_person_reaction())
            if emoji is not None:
                await poll_message.add_reaction(emoji)

        get_calendar().create_event(date, None, False)

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

    async def announce_results(
        self,
        date: datetime.date,
        time: datetime.time,
        in_person_happening: bool,
        message: discord.Message,
    ) -> None:
        if not await self.announce_result_wait.wait():
            return

        if get_calendar().create_event(date, time, in_person_happening):
            content = "New time found: " + time.strftime("%H:%M")
            if in_person_happening:
                content += "\nAnd it's happening in person!"
            await message.channel.send(content)

    # @override
    async def on_reaction_changed(self, message: discord.Message, reaction_added: bool) -> None:
        if not await self.update_message_wait.wait():
            return

        reactions = await found_reactions_cache.get_found_reactions(message)
        (date, in_person) = find_date_and_in_person(await message_cache.get_replied(message))

        if config.get_voting_cancel_reaction() in reactions and len(
            reactions[config.get_voting_cancel_reaction()]
        ):
            await message.edit(content="This poll was canceled", embed=None)
            get_calendar().delete_events(date)
            return

        (embed, time, in_person_happening) = self.get_embed_and_time(reactions, date, in_person)
        await message.edit(embed=embed)
        if time and self.last_result != (time, in_person_happening):
            self.last_result = (time, in_person_happening)
            asyncio.create_task(self.announce_results(date, time, in_person_happening, message))
