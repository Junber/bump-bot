import random
import discord

import bump_bot_config as config
from commands.command import BasicCommand

# The code in this file was externally provided and is used mostly as-is.
# Terms and conditions may apply

# rarities
C = "Common"
R = "Rare"
SR = "Secret Rare"
UR = "Ultra Rare"

# card library
# Base Game
BG01 = ["Animalistic Flesh Beast", C]
BG02 = ["Butcher", R]
BG03 = ["Butchering Flesh", R]
BG04 = ["Drunken Mosse", SR]
BG05 = ["Enraged Pig Butcher", R]
BG06 = ["Flesh Ball Thing", C]
BG07 = ["Flesh Drake", UR]
BG08 = ["Flesh Turtle", C]
BG09 = ["Joker", UR]
BG10 = ["Pig Butcher", C]
BG11 = ["Thrall", C]
BG12 = ["Winged Animalistic Flesh Beast", R]
BG13 = ["Fleshy Plains", R]
BG14 = ["Fort Dreadkeep", R]
BG15 = ["Combat Roll", C]
BG16 = ["Flesh Hacking", C]
BG17 = ["Flesh: Territorial Takeover", C]
BG18 = ["Ghoulian Greed", SR]
BG19 = ["Portal Swap", C]
BG20 = ["Watermelon", SR]
BG21 = ["Axolotl Wisdom", R]
BG22 = ["Create Weak Revenant", R]
BG23 = ["Ritualistic Offering", R]
BG24 = ["Suffering", SR]
BG25 = ["Bucket Helmet", SR]
BG26 = ["Chikage & Reiketsu", UR]
BG27 = ["Dual Blades", R]
BG28 = ["Flesh Horn", C]
BG29 = ["Iron Blades", C]
# Horrors Lurking in the Deep
HlitD01 = ["Captain Murdock", SR]
HlitD02 = ["Deep Dive Axolotl", SR]
HlitD03 = ["Flesh Doge", R]
HlitD04 = ["He", C]
HlitD05 = ["Seaweeds", C]
HlitD06 = ["Swift Swim Axolotl", C]
HlitD07 = ["The Leviathan", UR]
HlitD08 = ["Grand Ocean", R]
HlitD09 = ["Blood Spellbook", R]
HlitD10 = ["Loaded Barrel", C]
HlitD11 = ["One-and-done Armor", C]
HlitD12 = ["Barrel of Poshno Brew", C]
HlitD13 = ["Gamble Frigate", R]
HlitD14 = ["Bomb Vest", C]
# Legends I: Heroes of the  Order
L1HotO01 = ["Barbara", R]
L1HotO02 = ["Blanche", C]
L1HotO03 = ["Blanche: Assault Mode", SR]
L1HotO04 = ["Eileen", R]
L1HotO05 = ["Lennox", C]
L1HotO06 = ["Loran", UR]
L1HotO07 = ["Sir Horsi", C]
L1HotO08 = ["Vladimir Poshnovitz", C]
L1HotO09 = ["Lennox' Frog-Man-Communication", C]
L1HotO10 = ["Butchers' Forge", C]
# Meatier Grounds
MG01 = ["Joker's Apprentice", C]
MG02 = ["Laughing Servant", C]
MG03 = ["Psy Frog", R]
MG04 = ["Queen's Guard", C]
MG05 = ["Quick Flying Crow-People Raider", C]
MG06 = ["Sand Worm", UR]
MG07 = ["Spiky Frog", C]
MG08 = ["Axolotl River Torrents", C]
MG09 = ["Desert Holy Site", R]
MG10 = ["Nightmare Zone", SR]
MG11 = ["Blessing of Amidral", R]
MG12 = ["Joker Robe", R]
MG13 = ["Offering to the Flesh Drakes", SR]
MG14 = ["Trebuchet Arrow", C]
MG15 = ["Trebuchet Bolt", C]
MG16 = ["All-Out Attack", C]
MG17 = ["Blood Portal Stone", R]
MG18 = ["Trebuchet", R]
MG19 = ["Fushigiri", UR]
MG20 = ["Joking Daggers", R]
# Reaching for the Stars
RftS01 = ["Banshee", C]
RftS02 = ["Eyes", C]
RftS03 = ["Pirate", C]
RftS04 = ["Canvas of the Nightly Heavens", SR]
RftS05 = ["Blood Demanding Chalice", R]
RftS06 = ["The Shattering", UR]
RftS07 = ["Death", R]
RftS08 = ["Money", C]
RftS09 = ["Crap", C]
RftS10 = ["Impeding Blades", R]
RftS11 = ["Blasphemous Ritual", R]
RftS12 = ["Shadow", C]
RftS13 = ["Tree", C]
RftS14 = ["Wine", C]
RftS15 = ["Earth Scorcher", R]
RftS16 = ["Mushroom", C]
# Timeworn Empire
TE01 = ["Aquatic Enigma", SR]
TE02 = ["Crimson Guard", C]
TE03 = ["Imperiled Villagers", C]
TE04 = ["Inquisitor", R]
TE05 = ["Swift Serial Killer", C]
TE06 = ["Zealot of Life", R]
TE07 = ["Chaos", SR]
TE08 = ["The Last Vigil", UR]
TE09 = ["Flesh Drake Sighting", C]
TE10 = ["Jester's Flamboyant Spectacle", C]
TE11 = ["Malcontent of a God", R]
TE12 = ["Polluted Brine Flood", C]
TE13 = ["Religious Militia", C]
TE14 = ["Tax Evasion", C]
TE15 = ["Vigor of Ornstein", R]
TE16 = ["Crimson Prison", C]
TE17 = ["Electricity Orb", SR]
TE18 = ["Curse Mark", R]
TE19 = ["Flamboyant Robes", C]
TE20 = ["Wall of Thorns", C]


# booster packs
BG = [
    BG01,
    BG02,
    BG03,
    BG04,
    BG05,
    BG06,
    BG07,
    BG08,
    BG09,
    BG10,
    BG11,
    BG12,
    BG13,
    BG14,
    BG15,
    BG16,
    BG17,
    BG18,
    BG19,
    BG20,
    BG21,
    BG22,
    BG23,
    BG24,
    BG25,
    BG26,
    BG27,
    BG28,
    BG29,
]
MG = [
    MG01,
    MG02,
    MG03,
    MG04,
    MG05,
    MG06,
    MG07,
    MG08,
    MG09,
    MG10,
    MG11,
    MG12,
    MG13,
    MG14,
    MG15,
    MG16,
    MG17,
    MG18,
    MG19,
    MG20,
]
RftS = [
    RftS01,
    RftS02,
    RftS03,
    RftS04,
    RftS05,
    RftS06,
    RftS07,
    RftS08,
    RftS09,
    RftS10,
    RftS11,
    RftS12,
    RftS13,
    RftS14,
    RftS15,
    RftS16,
]
HlitD = [
    HlitD01,
    HlitD02,
    HlitD03,
    HlitD04,
    HlitD05,
    HlitD06,
    HlitD07,
    HlitD08,
    HlitD09,
    HlitD10,
    HlitD11,
    HlitD12,
    HlitD13,
    HlitD14,
]
L1HotO = [
    L1HotO01,
    L1HotO02,
    L1HotO03,
    L1HotO04,
    L1HotO05,
    L1HotO06,
    L1HotO07,
    L1HotO08,
    L1HotO09,
    L1HotO10,
]
TE = [
    TE01,
    TE02,
    TE03,
    TE04,
    TE05,
    TE06,
    TE07,
    TE08,
    TE09,
    TE10,
    TE11,
    TE12,
    TE13,
    TE14,
    TE15,
    TE16,
    TE17,
    TE18,
    TE19,
    TE20,
]
# BCC = [BCC01, BCC02, BCC03, BCC04, BCC05, BCC06, BCC07, BCC08, BCC09, BCC10, BCC11, BCC12, BCC13, BCC014, BCC015, BCC16]
# L2AoI = [L2AoI01, L2AoI02, L2AoI03, L2AoI04, L2AoI05, L2AoI06, L2AoI07, L2AoI08, L2AoI09, L2AoI10]

packs = {
    "A": BG,
    "B": MG,
    "C": RftS,
    "D": HlitD,
    "E": L1HotO,
    #'F': TE
}

booster_packs = {
    "A": "Base Game",
    "B": "Meatier Grounds",
    "C": "Reaching for the Stars",
    "D": "Horrors lurking in the Deep",
    "E": "Legends I: Heroes of the Order",
    "F": "Timeworn Empire",
    "G": "Bygone Centuary Chronicles",
    "H": "Legends II: Acolytes of Immortality",
    "I": "Adventure Memoirs",
    "J": "Infernal Mountain Wrath",
    "K": "Legends III: Current Era Trailblazers",
}


# Package Prize Calculator (Updated version; Allows for easier/quicker changes of prizes for individual packs or the market as a whole)
def PrizeTable(x):
    x = float(x)
    y = 4 * (1.5 * ((5 * x**4) / 24 - (25 * x**3) / 12 + (175 * x**2) / 24 - (5 * x) / 12))
    y = round(y)
    y = int(y)
    return str(y) + " Carnens"


prizes = {
    "A": PrizeTable(1),
    "B": PrizeTable(2),
    "C": PrizeTable(3),
    "D": PrizeTable(3),
    "E": PrizeTable(5),
    "F": PrizeTable(3),
    "G": PrizeTable(4),
    "H": PrizeTable(5),
    "I": PrizeTable(2),
    "J": PrizeTable(3),
    "K": PrizeTable(5),
}


# checking a booster pack for each card of a certain rarity
def RaritySearch(Liste, Rarity):
    Result = []
    for element in Liste:
        if element[1] == Rarity:
            Result.append(element)
    return Result


# pulling one card from a booster pack with a predetermined rarity
def CardPull(Liste, Rarity):
    Pool = RaritySearch(Liste, Rarity)
    random.shuffle(Pool)
    x = random.randint(0, len(Pool) - 1)
    return Pool[x]


def pull_pack(booster: str):
    # determining the rarity of the card pulled (Switches would probably be more effective than if-clauses)
    luck = random.randint(1, 100)
    Rarity = 0

    # assigning boosterpack chosen for the program to progress
    pack = packs[booster]

    # if-clause to determine how the card pulling should be done based on the selected booster pack
    if booster == "E":
        if luck <= 54:
            Rarity = C
        if luck > 54 and luck < 86:
            Rarity = R
        if luck >= 86 and luck < 98:
            Rarity = SR
        if luck > 97:
            Rarity = UR
        return [CardPull(pack, Rarity)]
    else:
        if luck <= 75:
            Rarity = R
        if luck > 75 and luck < 96:
            Rarity = SR
        if luck > 95:
            Rarity = UR
        return [CardPull(pack, C), CardPull(pack, C), CardPull(pack, Rarity)]


class BoosterSelect(discord.ui.Select):
    def __init__(self):
        options = []

        for pack in booster_packs:
            options.append(
                discord.SelectOption(
                    label="{} ({})".format(booster_packs[pack], prizes[pack]), value=pack
                )
            )

        super().__init__(placeholder="Choose booster pack...", options=options)

    async def callback(self, interaction: discord.Interaction):
        pack = self.values[0]
        cards = pull_pack(pack)
        card_text = "\n".join(["{} ({})".format(card[0], card[1]) for card in cards])
        await interaction.response.send_message(
            "{} paid {} to draw from {} and got:\n{}".format(
                interaction.user.display_name, prizes[pack], booster_packs[pack], card_text
            )
        )


def create_draw_view() -> discord.ui.View:
    view = discord.ui.View()
    view.add_item(BoosterSelect())
    return view


class CardCommand(BasicCommand):
    # @override
    def get_config(self) -> config.BasicCommandConfig:
        return config.get_cards()

    # @override
    async def on_message(self, message: discord.Message, channel: discord.TextChannel) -> None:
        await message.channel.send(self.get_message_content(), view=create_draw_view())
