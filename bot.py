import os
import time
from humanfriendly import format_timespan
import discord
import urllib.request
import json
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.ext.commands import CheckFailure
from discord.ext.commands.cooldowns import BucketType
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
bot = commands.Bot(command_prefix="!cast ", case_insensitive=True)
bot.remove_command("help")

TARGET_SERVER = "mc.koolkidz.club"
API_URL = "https://api.mcsrvstat.us/2/"

role = "caster"
denyStr = "**𝔜𝔬𝔲 𝔞𝔯𝔢 𝔫𝔬𝔱 𝔠𝔞𝔭𝔞𝔟𝔩𝔢 𝔬𝔣 𝔠𝔞𝔰𝔱𝔦𝔫𝔤!**\n**ʸᵒᵘ ᵐᵘˢᵗ ʰᵃᵛᵉ ᵗʰᵉ ʳᵒˡᵉ ᵒᶠ ᶜᵃˢᵗᵉʳ**"
servOn = "𝔗𝔲𝔯𝔫𝔦𝔫𝔤 𝔱𝔥𝔢 𝔰𝔢𝔯𝔳𝔢𝔯 𝔬𝔫\nᵀʰⁱˢ ᵐᵃʸ ᵗᵃᵏᵉ ᵃ ᶠᵉʷ ᵐⁱⁿᵘᵗᵉˢ"
servOff = "𝔗𝔲𝔯𝔫𝔦𝔫𝔤 𝔱𝔥𝔢 𝔰𝔢𝔯𝔳𝔢𝔯 𝔬𝔣𝔣\nᵀʰⁱˢ ᵐᵃʸ ᵗᵃᵏᵉ ᵃ ᶠᵉʷ ᵐⁱⁿᵘᵗᵉˢ"
spam = "𝔖𝔬𝔪𝔢𝔬𝔫𝔢 𝔥𝔞𝔰 𝔞𝔩𝔯𝔢𝔞𝔡𝔶 𝔠𝔞𝔰𝔱𝔢𝔡\n>>> You must wait for at least\n"
spam2 = " before someone casts again"
lack = "**𝔜𝔬𝔲 𝔩𝔞𝔠𝔨 𝔱𝔥𝔢 𝔠𝔞𝔭𝔞𝔟𝔦𝔩𝔦𝔱𝔶 𝔬𝔣 𝔠𝔞𝔰𝔱𝔦𝔫𝔤 𝔱𝔥𝔦𝔰 𝔠𝔬𝔪𝔪𝔞𝔫𝔡!**\n**ʸᵘʰ ᵃⁱⁿᵗ ᵃˡˡᵒʷᵉᵈ**"
stsErr = "**𝔊𝔬𝔡 𝔣𝔲𝔠𝔨𝔦𝔫 𝔡𝔞𝔪𝔪𝔦𝔱**\n>There has been an issue with getting that info"
plzwait = "𝔄𝔩𝔩𝔬𝔴 𝔪𝔢 𝔞 𝔰𝔢𝔠𝔬𝔫𝔡..."
unknown = "ℑ 𝔡𝔬𝔫'𝔱 𝔲𝔫𝔡𝔢𝔯𝔰𝔱𝔞𝔫𝔡"
whatStr = "𝔚𝔥𝔞𝔱.\n"
cfus = "𝔜𝔬𝔲 𝔰𝔢𝔢𝔪 𝔠𝔬𝔫𝔣𝔲𝔰𝔢𝔡\n"
helpStr = "ℌ𝔢𝔯𝔢 𝔞𝔯𝔢 𝔱𝔥𝔢 𝔠𝔲𝔯𝔯𝔢𝔫𝔱 𝔞𝔳𝔞𝔦𝔩𝔞𝔟𝔩𝔢 𝔠𝔞𝔰𝔱𝔰:```\nSwitch on|off : Turn the server on or off\nStatus : Get the status of the server```"

cache = ""
requestCool = 35  # Cooldown on API
requestTime = 0


def getSpamMsg(time):
    return spam + format_timespan(int(time)) + spam2


def formatAPImsg(data):
    final = "```\n"
    final += (
        data["hostname"]
        + " is currently "
        + ("online" if data["online"] else "offline")
    )

    # if "motd" in data:
    #     final += " " + data["motd"]["clean"]
    if "players" in data:
        final += " Players online: " + str(data["players"]["online"])
    final += (
        "\nlast update: " + format_timespan(int(time.time()) - requestTime) + " ago"
    )
    final += "\n```"
    return final


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
        return stsErr
    return formatAPImsg(data)


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


@bot.command(name="what", help="uhhhhhhhhh")
async def what(ctx):
    response = "**𝔧𝔬𝔢 𝔐𝔄𝔪𝔞𝔐𝔄 ℌ𝔥𝔞𝔥𝔞𝔥𝔞ℌ𝔞**"
    await ctx.send(response)


# @bot.command(name="turnOn", help="Turn on the server")
# @commands.has_role("Caster")
# @commands.cooldown(1, 120, BucketType.default)
# @commands.max_concurrency(1, per=BucketType.default, wait=False)
# async def turnOn(ctx):
#     refreshCommands(ctx)
#     response = servOn
#     await ctx.send(response)


# @bot.command(name="turnOff", help="Turn off the server")
# @commands.has_role("Caster")
# @commands.cooldown(1, 120, BucketType.default)
# @commands.max_concurrency(1, per=BucketType.default, wait=False)
# @commands.is_owner()
# async def turnOff(ctx):
#     refreshCommands(ctx)
#     response = servOff
#     await ctx.send(response)


@bot.command(name="help")
async def help(ctx):
    await ctx.send(helpStr)


@bot.command(
    name="switch",
    help="'!cast switch on' If you are Caster\n'!cast switch off' If you are Owner",
)
@commands.has_role("Caster")
@commands.cooldown(1, 120, BucketType.default)
@commands.max_concurrency(1, per=BucketType.channel, wait=False)
# @commands.is_owner()
async def switch(ctx, state: str = None):
    if state == None:
        await ctx.send(cfus + helpStr)
        return

    if state == "on":
        response = servOn
        await ctx.send(response)
        return

    if state == "off":
        if commands.is_owner():
            response = servOff
            await ctx.send(response)
        else:
            raise commands.NotOwner

    raise commands.UserInputError("whaaat")


# Check if server is actually up and running
def refreshCommands(ctx):
    # turnOn.reset_cooldown(ctx)
    # turnOff.reset_cooldown(ctx)
    return


@bot.command(name="status", help="Check the status of the server")
async def status(ctx):
    if APIWillUpdate():
        await ctx.send(plzwait)
    response = getAltStatus()
    await ctx.send(response)


@bot.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, "on_error"):
        return

    error = getattr(error, "original", error)

    cool = (commands.CommandOnCooldown, commands.MaxConcurrencyReached)
    role = commands.MissingRole
    owner = commands.NotOwner
    helpy = (commands.UserInputError, commands.CommandNotFound)

    if isinstance(error, helpy):
        time.sleep(1)
        await ctx.send(whatStr)
        time.sleep(3)
        await ctx.send(cfus)
        time.sleep(2)
        await ctx.send(helpStr)
        refreshCommands(ctx)

    if isinstance(error, cool):
        await ctx.send(getSpamMsg(error.retry_after))

    if isinstance(error, role):
        await ctx.send(denyStr)

    if isinstance(error, owner):
        await ctx.send(lack)

    if isinstance(error, commands.BadArgument):
        await ctx.send(unknown)


# @bot.event
# async def on_error(event, *args, **kwargs):
#     with open("err.log", "a") as f:
#         if event == "on_message":
#             f.write(f"Unhandled message: {args[0]}\n")
#         else:
#             raise


bot.run(TOKEN)
