import datetime
from typing import Tuple
import discord

import bump_bot_config as config
from calendar_client import get_calendar
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


def find_date(weekday_index: int, message_date: datetime.date) -> datetime.date:
    date = message_date + datetime.timedelta(weekday_index - message_date.weekday())
    if weekday_index < message_date.weekday():
        date += datetime.timedelta(7)
    return date


def find_date_and_in_person(
    argument: str, message_date: datetime.date
) -> tuple[datetime.date, bool]:
    weekday_index = find_closest_index(WEEKDAYS, argument.lower())
    in_person = WEEKDAYS[weekday_index] in config.get_bump_time_in_person_days()
    date = find_date(weekday_index, message_date)
    return (date, in_person)


class BumpTimeCommand(VotingCommand):
    @staticmethod
    def get_embed_and_time(
        found_reactions: found_reactions_cache.FoundReactions, in_person: bool
    ) -> Tuple[discord.Embed, datetime.time | None, bool]:
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

        embed = discord.Embed(title=config.get_bump_time_embed_title().format()).add_field(
            name=config.get_bump_time_embed_field_name(), value=message_text
        )

        earliest_datetime = None
        if len(members_who_voted) >= config.get_required_votes():
            earliest_datetime = datetime.time.fromisoformat(earliest_possible_time)

        return (embed, earliest_datetime, in_person_happening)

    @staticmethod
    def get_start_poll_command(day: str) -> str:
        return config.get_voting_trigger() + " " + day

    @staticmethod
    async def start_time_poll(message: discord.Message, channel: discord.TextChannel) -> None:
        # TODO: avoid creating new instance here
        await BumpTimeCommand().on_message(message, channel)

    @staticmethod
    def handles_message_static(message: discord.Message, channel: discord.TextChannel) -> bool:
        return (
            channel.name == config.get_voting_channel_name()
            and message.content.lower() != config.get_voting_trigger()
            and message.content.lower().startswith(config.get_voting_trigger())
        )

    # @override
    async def handles_message(self, message: discord.Message, channel: discord.TextChannel) -> bool:
        return self.handles_message_static(message, channel)

    # @override
    async def send_poll(self, message: discord.Message) -> discord.Message:
        argument = message.content[len(config.get_voting_trigger()) :].strip()
        content = (
            config.get_bump_time_message_content_prefix()
            + argument
            + config.get_bump_time_message_content_postfix()
        )
        (date, in_person) = find_date_and_in_person(argument, datetime.date.today())
        (embed, _, _) = self.get_embed_and_time({}, in_person)
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
        (date, in_person) = find_date_and_in_person(argument, message.created_at.date())

        if config.get_voting_cancel_reaction() in reactions and len(
            reactions[config.get_voting_cancel_reaction()]
        ):
            await message.edit(content="This poll was canceled", embed=None)
            get_calendar().delete_events(date)
            return

        (embed, time, in_person_happening) = self.get_embed_and_time(reactions, in_person)
        await message.edit(embed=embed)

        if time and get_calendar().create_event(date, time, in_person_happening):
            content = "New time found: " + time.strftime("%H:%M")
            if in_person_happening:
                content += "\nAnd it's happening in person!"
            await message.channel.send(content)
