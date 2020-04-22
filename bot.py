import json
import os
import time
import urllib.request

import discord
from discord.ext import commands
from discord.ext.commands import CheckFailure, has_permissions
from discord.ext.commands.cooldowns import BucketType
from dotenv import load_dotenv
from humanfriendly import format_timespan

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
BOTCOLOR = 0xBA51F7
BOTROLE = "caster"
bot = commands.Bot(command_prefix="!cast ", case_insensitive=True)
bot.remove_command("help")

TARGET_SERVER = "mc.koolkidz.club"
API_URL = "https://api.mcsrvstat.us/2/"

cache = ""
requestCool = 35  # Cooldown on API
requestTime = 0


ABCs = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


class FONT:
    goth = {
        ord(s): d
        for s, d in zip(ABCs, "𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷")
    }
    gothBold = {
        ord(s): d
        for s, d in zip(ABCs, "𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟")
    }
    smol = {
        ord(s): d
        for s, d in zip(ABCs, "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾQᴿˢᵀᵁⱽᵂˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖqʳˢᵗᵘᵛʷˣʸᶻ")
    }
    math = {
        ord(s): d
        for s, d in zip(ABCs, "𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃")
    }


# SPEECH
# mumble
# -------
#   info
# -------
# foot


def getEmbedded(
    speech="", mumble="‎", info="‎", foot="", smallMumble=False, smallFoot=False
):
    try:
        speech = str(speech).translate(FONT.goth)
        if smallFoot:
            foot = str(foot).translate(FONT.smol)
        if str(info) != "‎":  # info has a blank unicode as it's default
            info = "```\n" + str(info) + "\n```"
        # else:
        #     info = mumble
        #     mumble = "‎" # blank unicode
        if str(mumble) != "‎":  # mumble has a blank unicode as it's default
            if smallMumble:
                mumble = str(mumble).translate(FONT.smol)
            else:
                mumble = str(mumble)

        embed = discord.Embed(title=speech, color=BOTCOLOR)  # , description=""
        embed.add_field(name=mumble, value=info)

        if foot != "":
            embed.set_footer(text=foot)
        return embed
    except Exception as e:
        print(e)


def spamMsg(time):
    return getEmbedded(
        "Someone has already casted",
        info="You must wait for at least "
        + format_timespan(int(time))
        + " before someone casts again",
    )


class BOTMSG:
    class embed:
        caster = getEmbedded(
            "***You are not capable of casting!***",
            "**you must have the role of caster**",
        )
        serverOn = getEmbedded("Turning the server on", "This may take a few minutes")
        serverOff = getEmbedded("Turning the server off", "This may take a few minutes")
        lack = getEmbedded(
            "**You lack the capability of casting this commmand**",
            "Yuh aint allowed",
            smallMumble=True,
        )
        error = getEmbedded(
            "**God fuckin dammit**",
            "not this shit again",
            "There has been an issue with getting that info",
            "fuck",
            True,
        )
        helper = getEmbedded(
            "Here are the current available casts",
            info="Turn on|off : Turn the server on or off\nSwitch on|off : Same as Turn\nStatus : Get the status of the server\nHelp: Show this message",
            foot="not case sensitive btw",
        )
        errorHelp = getEmbedded(
            "Allow me to remind you about the available casts",
            info="Turn on|off : Turn the server on or off\nSwitch on|off : Same as Turn\nStatus : Get the status of the server\nHelp: Show this message",
            foot="not case sensitive btw",
        )

    give = "Here ya go"
    wait = "Allow me a second".translate(FONT.goth) + "..."
    what = "What. \n".translate(FONT.goth)
    unknown = "I don't understand".translate(FONT.goth)
    confused = "You seem confused".translate(FONT.goth)


def formatAPImsg(data):
    final = (
        data["hostname"]
        + " is currently "
        + ("online" if data["online"] else "offline")
    )

    # if "motd" in data:
    #     final += " " + data["motd"]["clean"]
    if "players" in data:
        final += " Players online: " + str(data["players"]["online"])
    curr = int(time.time())
    apiUpdate = data["debug"]["cachetime"]
    if apiUpdate == 0:
        apiUpdate = curr
    lastapiUpdate = format_timespan(curr - apiUpdate + curr - requestTime)
    lastUpdate = "last update: " + lastapiUpdate + " ago"
    return getEmbedded(BOTMSG.give, lastUpdate, final, "mcsrvstat.us")


def APIWillUpdate():
    return int(time.time()) - requestTime > requestCool


def getAltStatus(data=None):
    global cache, requestTime
    try:
        if not data:
            if APIWillUpdate():
                print("Updating API data")
                with urllib.request.urlopen(API_URL + TARGET_SERVER) as url:
                    requestTime = int(time.time())
                    data = json.loads(url.read().decode())
                    cache = data
            else:
                return getAltStatus(cache)
    except Exception as e:
        print(e)
        return BOTMSG.embed.error
    return formatAPImsg(data)


@bot.event
async def on_ready():
    print(f"{bot.user.name} has landed")


@bot.command(name="help")
async def help(ctx):
    await ctx.send(embed=BOTMSG.embed.helper)


@bot.command(name="clear")
@commands.is_owner()
async def clear(ctx):
    await ctx.send(
        "‎\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n‎"
    )


@bot.command(name="turn")
@commands.has_role("Caster")
@commands.cooldown(1, 120, BucketType.default)
@commands.max_concurrency(1, per=BucketType.channel, wait=False)
async def turn(ctx, state: str = None):
    if state == None:
        await ctx.send(embed=BOTMSG.embed.errorHelp)
        return

    if state == "on":
        await ctx.send(embed=BOTMSG.embed.serverOn)
        return

    if state == "off":
        if commands.is_owner():
            await ctx.send(embed=BOTMSG.embed.serverOff)
        else:
            raise commands.NotOwner
        return

    raise commands.UserInputError("Issue with 'Turn' command", state)


@bot.command(name="switch", pass_context=True)
async def switch(ctx):
    await turn.invoke(ctx)


# TODO: Check if server is actually up and running then reset cooldown if so
def refreshCommands(ctx):
    # turnOn.reset_cooldown(ctx)
    # turnOff.reset_cooldown(ctx)
    return


@bot.command(name="status")
async def status(ctx):
    if APIWillUpdate():
        await ctx.send(BOTMSG.wait)
    response = getAltStatus()
    await ctx.send(embed=response)


@bot.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, "on_error"):
        return

    print(error)
    error = getattr(error, "original", error)
    print(error)

    cool = (commands.CommandOnCooldown, commands.MaxConcurrencyReached)
    role = commands.MissingRole
    owner = commands.NotOwner
    helpy = (commands.UserInputError, commands.CommandNotFound)

    if isinstance(error, helpy):
        time.sleep(1)
        await ctx.send(BOTMSG.what)
        time.sleep(2)
        await ctx.send(BOTMSG.confused)
        time.sleep(1)
        await ctx.send(embed=BOTMSG.embed.errorHelp)
        refreshCommands(ctx)

    if isinstance(error, cool):
        await ctx.send(embed=spamMsg(error.retry_after))

    if isinstance(error, role):
        await ctx.send(embed=BOTMSG.embed.caster)

    if isinstance(error, owner):
        await ctx.send(embed=BOTMSG.embed.lack)

    if isinstance(error, commands.BadArgument):
        await ctx.send(BOTMSG.unknown)


bot.run(TOKEN)
