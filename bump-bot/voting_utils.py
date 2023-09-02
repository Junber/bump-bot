import discord


def raw_member_list(members: set[discord.Member]) -> str:
    result = ""
    for member in sorted(members, key=lambda x: x.display_name):
        result += member.display_name
        result += ", "
    return result.removesuffix(", ")


def member_list(
    members: set[discord.Member], members_who_voted: set[discord.Member], empty: str
) -> str:
    if len(members) == 0:
        return empty
    elif len(members) <= len(members_who_voted) / 2:
        return raw_member_list(members)
    elif len(members) < len(members_who_voted):
        return "**NOT** " + raw_member_list(members_who_voted.difference(members))
    elif len(members) == len(members_who_voted):
        return "Everyone!"
    else:
        return "[Internal error]"
