from abc import abstractmethod
import asyncio
import functools
from typing import Any, Callable, Coroutine, override
import discord

from cancelable_wait import CancelableWait
from commands.command import ReactionsCommand


# TODO: Extract more common functionality to this class
class VotingCommand(ReactionsCommand):
    update_message_wait = CancelableWait(1.0)

    @staticmethod
    async def replace_pins(
        channel: discord.TextChannel,
        new_pin_function: Callable[[], Coroutine[Any, Any, discord.Message]],
    ) -> None:
        async with asyncio.TaskGroup() as tg:
            for pinned in await channel.pins():  # TODO: Cache pins?
                tg.create_task(pinned.unpin())
            new_message = await new_pin_function()
            tg.create_task(new_message.pin())

    @staticmethod
    def raw_member_list(members: set[discord.Member]) -> str:
        result = ""
        for member in sorted(members, key=lambda x: x.display_name):
            result += member.display_name
            result += ", "
        return result.removesuffix(", ")

    @staticmethod
    def member_list(
        members: set[discord.Member], members_who_voted: set[discord.Member], empty: str
    ) -> str:
        if len(members) == 0:
            return empty
        elif len(members) <= len(members_who_voted) / 2:
            return VotingCommand.raw_member_list(members)
        elif len(members) < len(members_who_voted):
            return "**NOT** " + VotingCommand.raw_member_list(members_who_voted.difference(members))
        elif len(members) == len(members_who_voted):
            return "Everyone!"
        else:
            return "[Internal error]"

    @abstractmethod
    async def send_poll(
        self, message: discord.Message, channel: discord.TextChannel
    ) -> discord.Message:
        pass

    @override
    async def on_message(self, message: discord.Message, channel: discord.TextChannel) -> None:
        await self.replace_pins(
            channel,
            functools.partial(self.send_poll, message, channel),
        )
