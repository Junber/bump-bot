import logging
from typing import AsyncGenerator, Iterable
import discord
import pylev  # type: ignore

logger = logging.getLogger("bump_bot")
logger.setLevel(logging.DEBUG)


def get_logger() -> logging.Logger:
    return logger


def find_closest_index(options: Iterable[str], to_find: str) -> int:
    closest_distance = 99999
    closest_index = -1
    for index, option in enumerate(options):
        distance = pylev.levenshtein(option, to_find)
        if distance < closest_distance:
            closest_distance = distance
            closest_index = index
    return closest_index


async def get_all_message(
    channel: discord.TextChannel,
) -> AsyncGenerator[discord.Message, None]:
    last_message = None
    found = True
    while found:
        found = False
        async for message in channel.history(before=last_message):
            yield message
            last_message = message
            found = True
