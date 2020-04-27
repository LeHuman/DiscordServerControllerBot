import json
import os
import random
import time
import urllib.request
import powerSwitch as PS

import discord
from discord.ext import commands
from discord.ext.commands import CheckFailure, has_permissions
from discord.ext.commands.cooldowns import BucketType
from dotenv import load_dotenv
from humanfriendly import format_timespan

load_dotenv()
TARGET_SERVER = os.getenv("TARGET_SERVER")
API_URL = os.getenv("API_URL")
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
BOTFONT = os.getenv("BOTFONT")
BOTCOLOR = int(os.getenv("BOTCOLOR"), 16)
BOTROLE = os.getenv("BOTROLE")
BOTNAME = os.getenv("BOTNAME")
BOTCOOLDOWN = int(os.getenv("SERVER_WAIT_POWER")) * 60  # Minimum wait time until we attempt to ping the server
bot = commands.Bot(command_prefix="!cast ", case_insensitive=True)
bot.remove_command("help")

cache = ""
requestCool = 35  # Cooldown on API
requestTime = 0

ABCs = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


class FONT:
    goth = {ord(s): d for s, d in zip(ABCs, "𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷")}
    gothBold = {ord(s): d for s, d in zip(ABCs, "𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟")}
    smol = {ord(s): d for s, d in zip(ABCs, "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾQᴿˢᵀᵁⱽᵂˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖqʳˢᵗᵘᵛʷˣʸᶻ")}
    math = {ord(s): d for s, d in zip(ABCs, "𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃")}
    band = {ord(s): d for s, d in zip(ABCs, "ᗩᗷᑕᗪEᖴGᕼIᒍKᒪᗰᑎOᑭᑫᖇᔕTᑌᐯᗯ᙭YᘔᗩᗷᑕᗪEᖴGᕼIᒍKᒪᗰᑎOᑭᑫᖇᔕTᑌᐯᗯ᙭Yᘔ")}
    mono = {ord(s): d for s, d in zip(ABCs, "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣")}
    choice = {
        "goth": goth,
        "gothBold": gothBold,
        "smol": smol,
        "math": math,
        "band": band,
        "mono": mono,
    }


SPEECHFONT = FONT.choice[BOTFONT] if BOTFONT in FONT.choice else FONT.goth


def getEmbedded(speech="", mumble="‎", info="‎", foot="", smallMumble=False, smallFoot=False, ctx=None):
    speech = str(speech).translate(SPEECHFONT)
    if smallFoot:
        foot = str(foot).translate(FONT.smol)
    if str(info) != "‎":  # info has a blank unicode as it's default
        info = "```\n" + str(info) + "\n```"
    if str(mumble) != "‎":  # mumble has a blank unicode as it's default
        if smallMumble:
            mumble = str(mumble).translate(FONT.smol)
        else:
            mumble = str(mumble)

    embed = discord.Embed(title=speech, color=BOTCOLOR, description=ctx.message.author.mention if ctx else "")
    embed.add_field(name=mumble, value=info)

    if foot != "":
        embed.set_footer(text=foot)
    return embed


def getEmbeddedFactory(
    speechStr="", mumbleStr="‎", infoStr="‎", footStr="", smallMumble=False, smallFoot=False,
):
    # What final func should request
    rSpch = speechStr == ""
    rMmbl = mumbleStr == "‎"
    rInfo = infoStr == "‎"
    rFoot = footStr == ""

    if not rSpch:
        speechStr = str(speechStr).translate(SPEECHFONT)

    if not rMmbl:
        if smallMumble:
            mumbleStr = str(mumbleStr).translate(FONT.smol)
        else:
            mumbleStr = str(mumbleStr)

    if not rInfo:
        infoStr = "```\n" + str(infoStr) + "\n```"

    if not rFoot:
        if smallFoot:
            footStr = str(footStr).translate(FONT.smol)
        else:
            footStr = str(footStr)

    def embedLoad(ctx=None, speech="", mumble="‎", info="‎", foot=""):
        embed = discord.Embed(
            title=str(speech).translate(SPEECHFONT) if rSpch else speechStr,
            color=BOTCOLOR,
            description=ctx.message.author.mention if ctx else "",
        )
        embed.add_field(
            name=mumble if rMmbl and str(mumble) != "‎" else mumbleStr,
            value="```\n" + str(info) + "\n```" if rInfo and str(info) != "‎" else infoStr,
            inline=True,
        )
        if footStr != "":
            embed.set_footer(text=footStr)
        elif foot != "":
            embed.set_footer(text=foot)
        return embed

    return embedLoad


def spamMsg(time, ctx):
    return getEmbedded(
        "Someone has already casted this",
        "Use the status command to check current status",
        "You must wait for at least " + format_timespan(int(time)) + " before someone casts again",
        ctx=ctx,
    )


class BOTMSG:
    class embed:
        __HelpString = """
Turn on|off : Turn the server on or off
Switch on|off : Same as Turn
Status : Get the status of the server
Spec : Get server specifications
Help: Show this message"""
        caster = getEmbeddedFactory("***You are not capable of casting!***", "**you must have the role of caster**")
        serverOn = getEmbeddedFactory("Turning the server on", "This may take a few minutes")
        serverOff = getEmbeddedFactory("Turning the server off", "This may take a few minutes")
        lack = getEmbeddedFactory("**You lack the capability of casting this commmand**", "Yuh aint allowed", smallMumble=True,)
        error = getEmbeddedFactory(
            "**God fuckin dammit**",
            "not this shit again",
            "There has been an issue\nPlease, report this issue\nto the issuing department\n\t\t\t\tThank you",
            "fuck",
            True,
        )
        warning = getEmbeddedFactory("There may be an issue", "Report this issue to owner")
        helper = getEmbeddedFactory(
            "Here are the current available casts", "All prefixed with !cast ", __HelpString, "not case sensitive btw",
        )
        errorHelp = getEmbeddedFactory(
            "Allow me to remind you about the available casts", "All prefixed with !cast ", __HelpString, "not case sensitive btw",
        )
        spec = getEmbeddedFactory("Here is what I see")
        specificHelp = getEmbeddedFactory("You haved incorrectly casted")

    give = "Here ya go"
    wait = "Allow me a second".translate(SPEECHFONT)
    what = "What. \n".translate(SPEECHFONT)
    unknown = "I don't understand".translate(SPEECHFONT)
    confused = "You seem confused".translate(SPEECHFONT)


def formatAPImsg(ctx, data):
    final = data["hostname"] + " is currently " + ("online" if data["online"] else "offline")

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
    return getEmbedded(BOTMSG.give, lastUpdate, final, "mcsrvstat.us", ctx=ctx)


def APIWillUpdate():
    return int(time.time()) - requestTime > requestCool


def getAltStatus(ctx, data=None):
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
                return getAltStatus(ctx, cache)
    except Exception as e:
        print(e)
        return BOTMSG.embed.error(ctx)
    return formatAPImsg(ctx, data)


async def sendFinalCommand(ctx, cmd):
    final = False
    if await PS.canSend():
        final = await PS.sendCommand(cmd)
    else:
        return "Warning: Server indicates that it has already sent\na command and is still awaiting a response"

    if final == -1:
        return "Error: uhm, im not sure how this happened.\nPlease report this issue to our issuing department"

    status = await PS.status()
    stsWarn = "Warning: "
    if status["timeout"]:
        stsWarn += "The last command sent never recieved a response from the server"
    if status["mismatch"]:
        stsWarn += ("\n" if status["timeout"] else "") + "Server indicates that there may be a network issue"
    if stsWarn != "Warning: ":
        return stsWarn
    return


@bot.event
async def on_ready():
    print(f"{bot.user.name} has landed")


@bot.command(name="help")
async def help(ctx):
    await ctx.send(embed=BOTMSG.embed.helper(ctx))


@bot.command(name="turn")
@commands.has_role("Caster")
@commands.cooldown(1, BOTCOOLDOWN, BucketType.default)
@commands.max_concurrency(1, per=BucketType.channel, wait=False)
async def turn(ctx, state: str = None):
    if ctx == 0:
        return
    if not await PS.canSend():
        await ctx.send(
            embed=BOTMSG.embed.warning(
                ctx, info="Server indicates that it has already sent\na command and is still awaiting a response\nPlease try again later"
            )
        )
        turn.reset_cooldown(ctx)
        return
    if state == "on":
        info = await sendFinalCommand(ctx, state)
        if info:
            await ctx.send(embed=BOTMSG.embed.serverOn(ctx, info=info))
        else:
            await ctx.send(embed=BOTMSG.embed.serverOn(ctx))
        return
    elif state == "off":
        if commands.is_owner():
            info = await sendFinalCommand(ctx, state)
            if info:
                await ctx.send(embed=BOTMSG.embed.serverOn(ctx, info=info))
            else:
                await ctx.send(embed=BOTMSG.embed.serverOn(ctx))
        else:
            raise commands.NotOwner
        return
    else:
        turn.reset_cooldown(ctx)
        await ctx.send(
            embed=BOTMSG.embed.specificHelp(
                ctx,
                mumble=f"{ctx.invoked_with.title()} command: ",
                info=f"{ctx.invoked_with.title()} must be followed by an 'on' or 'off'\nEx: !cast {ctx.invoked_with.title()} on",
            )
        )
        return

    raise commands.UserInputError("Issue with 'Turn' command", state)


@bot.command(name="switch", pass_context=True)
async def switch(ctx):
    await turn.invoke(ctx)


@bot.command(name="spec")
async def spec(ctx):
    specs = await PS.getSpecs()
    await ctx.send(embed=BOTMSG.embed.spec(ctx, info=specs, mumble=f"{BOTNAME} powered by Rpi0 v1.3"))


@bot.command(name="status")
async def status(ctx):
    if APIWillUpdate():
        await ctx.send(BOTMSG.wait + " " + ctx)
    response = getAltStatus(ctx)
    await ctx.send(embed=response)


@bot.command(name="error")
@commands.is_owner()
async def error(ctx):
    await ctx.send(embed=BOTMSG.embed.error(ctx))


@bot.command(name="clear")
@commands.is_owner()
async def clear(ctx):
    await ctx.send("‎\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n‎")


helpyRun = False


@bot.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, "on_error"):
        return

    print(error)
    error = getattr(error, "original", error)

    cool = (commands.CommandOnCooldown, commands.MaxConcurrencyReached)
    role = commands.MissingRole
    owner = commands.NotOwner
    helpy = (commands.UserInputError, commands.CommandNotFound)

    if isinstance(error, helpy):
        global helpyRun
        if not helpyRun:
            helpyRun = True
            if random.randint(0, 100) < 30:
                await ctx.send(BOTMSG.what)
                time.sleep(2)
            if random.randint(0, 100) < 55:
                await ctx.send(BOTMSG.confused + " " + ctx)
            await ctx.send(embed=BOTMSG.embed.errorHelp(ctx))
            helpyRun = False
        else:
            return

    if isinstance(error, cool):
        await ctx.send(embed=spamMsg(error.retry_after, ctx))

    if isinstance(error, role):
        await ctx.send(embed=BOTMSG.embed.caster(ctx))

    if isinstance(error, owner):
        await ctx.send(embed=BOTMSG.embed.lack(ctx))

    if isinstance(error, commands.BadArgument):
        await ctx.send(BOTMSG.unknown)


bot.run(TOKEN)
