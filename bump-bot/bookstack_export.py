import asyncio
from typing import AsyncGenerator
import discord
import pylev

from utils import find_closest_index, get_all_message
from bookstack_client import bookstack
import bump_bot_config as config
import discord_client
from utils import get_logger
import found_reactions_cache

# TODO: Move into config?
formats = [
    "**{}:**",
    "**{} :**",
    "**{}: **",
    "**{}**:",
    "**{} **:",
    "**{}** :",
    "**{}**",
    "*{}:*",
    "*{}: *",
    "*{}*:",
    "{}:",
    "{} :",
]
extract_description = [
    ("Name", "name"),
    ("Type", "type"),
    ("Effect", "effect"),
    ("Effect/Ability", "effect"),
    ("Special Effect", "effect"),
    ("Flavor Text", "flavor"),
    ("Flavour Text", "flavor"),
    ("Flavor", "flavor"),
    ("Flavour", "flavor"),
    ("Description", "flavor"),
    ("Cost", "cost"),
]
chapters = {
    "Artifact": ("Artifacts", ""),
    "Artefact": ("Artifacts", ""),
    "Weapon": ("Weapons", ""),
    "Weapon / Artefact": ("Weapons", ""),
    "Weapon + Spell tomb/catalyst": ("Weapons", ""),
    "Spellbook": ("Weapons", "Spell books"),
    'Unique "Spellbook"': ("Weapons", "Spell books"),
    "Armor": ("Armor", ""),
    "Item": ("Items", ""),
    "Item (reusable)": ("Items", "Reuseable"),
    "Food/Buff": ("Items", "Food"),
    "(Food) Item": ("Items", "Food"),
    "Item (Food)": ("Items", "Food"),
    "Cartomancy Card": ("Items", "Cartomancy Card"),
    "Hat": ("Hats", ""),
    "Hat-Artefact": ("Hats", ""),
    "Vomit Spell": ("Vomit Spells", ""),
    "Vomit Utility Spell": ("Vomit Spells", "Utility"),
    "Blood Spell": ("Blood Spells", ""),
    "Blood Spell, utility": ("Blood Spells", "Utility"),
    "Summon Spell": ("Blood Spells", ""),
    "? Spell": ("Blood Spells", ""),
    "Bone Spell": ("Bone Spells", ""),
    "Pet (I've heard those exist now?)": ("Pets", ""),
    "Artefact / Weapon / Item / Hat / Pet / Mystery": ("Pets", ""),
}
max_parse_distance = 3


def prefix_levenshtein(prefix: str, string: str) -> int:
    return pylev.levenshtein(prefix.lower(), string.lower()[: min(len(prefix), len(string))])


def extract(line: str) -> tuple[int, str, str]:
    best_distance = 99999
    best_result_name = ""
    best_line = ""
    for base_prefix, result_name in extract_description:
        for format in formats:
            prefix = format.format(base_prefix)
            distance = prefix_levenshtein(prefix, line)
            if distance < best_distance:
                best_distance = distance
                best_result_name = result_name
                best_line = line[len(prefix) :].strip()

    return best_distance, best_result_name, best_line


def parse(message: str) -> dict:
    result = {}
    last_result_name = ""
    for line in message.split("\n"):
        found = False
        distance, result_name, extracted = extract(line)
        if distance <= max_parse_distance:
            if result_name in result:
                result[result_name] += "  \n" + extracted
            else:
                result[result_name] = extracted
            last_result_name = result_name
            found = True
            break
        if not found:
            result[last_result_name] += "  \n" + line.strip()
    return result


def find_chapter(type: str) -> tuple[str, str]:
    keys = list(chapters.keys())
    return chapters[keys[find_closest_index(keys, type)]]


def export(message: str) -> bool:
    try:
        parsed = parse(message)
        markdown = "#### Effect\n{}".format(parsed["effect"])
        if "flavor" in parsed:
            markdown = "#### Flavor\n{}\n{}".format(parsed["flavor"], markdown)
        if "cost" in parsed:
            markdown = "{}\n#### Cost\n{}".format(markdown, parsed["cost"])

        bookstack.create_page(parsed["name"], markdown, find_chapter(parsed["type"]))
    except Exception:
        get_logger().exception("Parsing message failed:\n" + message)
        return False
    return True


def unexport(message: str) -> bool:
    try:
        parsed = parse(message)
        bookstack.delete_page(parsed["name"], find_chapter(parsed["type"]))
    except Exception:
        get_logger().exception("Parsing message failed:\n" + message)
        return False
    return True


async def has_reaction(message: discord.Message, emoji_string: str):
    reactions = await found_reactions_cache.get_found_reactions(message, True)
    for reaction in reactions:
        if reaction == emoji_string and len(reactions[reaction]):
            return True
    return False


async def export_if_needed(message: discord.Message) -> None:
    if await has_reaction(message, config.get_bookstack_exported_emoji()):
        return
    if export(message.content):
        emoji = discord_client.get_emoji(config.get_bookstack_exported_emoji())
        if emoji is not None:
            await message.add_reaction(emoji)


async def unexport_if_needed(message: discord.Message) -> None:
    if not await has_reaction(message, config.get_bookstack_exported_emoji()):
        return

    emoji = discord_client.get_emoji(config.get_bookstack_exported_emoji())
    client_user = discord_client.get_client().user
    if emoji is None or client_user is None:
        return

    if unexport(message.content):
        emoji = discord_client.get_emoji(config.get_bookstack_exported_emoji())
        if emoji is not None:
            await message.remove_reaction(emoji, client_user)


async def export_all(channel: discord.TextChannel) -> None:
    async with asyncio.TaskGroup() as tg:
        async for message in get_all_message(channel):
            if message.type == discord.MessageType.default and await has_reaction(
                message, config.get_bookstack_trigger()
            ):
                tg.create_task(export_if_needed(message))


async def unexport_all(channel: discord.TextChannel) -> None:
    async with asyncio.TaskGroup() as tg:
        async for message in get_all_message(channel):
            if message.type == discord.MessageType.default and await has_reaction(
                message, config.get_bookstack_trigger()
            ):
                tg.create_task(unexport_if_needed(message))


async def clear_emoji(channel: discord.TextChannel) -> None:
    emoji = discord_client.get_emoji(config.get_bookstack_exported_emoji())
    client_user = discord_client.get_client().user
    if emoji is None or client_user is None:
        return

    async with asyncio.TaskGroup() as tg:
        async for message in get_all_message(channel):
            if message.type == discord.MessageType.default and await has_reaction(
                message, config.get_bookstack_exported_emoji()
            ):
                tg.create_task(message.remove_reaction(emoji, client_user))
