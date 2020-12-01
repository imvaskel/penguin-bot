import discord
from discord.ext import commands
import os 
import sys, traceback
import json
import configparser
import aiohttp
import datetime
from aiogoogletrans import Translator
from asyncdagpi import Client
from utils.CustomBot import PenguinBot


startup_extensions = ['cogs.members', 'cogs.owner', 'cogs.moderator', 'cogs.fun', "jishaku", "cogs.mute", 'cogs.animals', 'cogs.listener', 'cogs.help_command', 'cogs.images']

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True" 

intents = discord.Intents.all()

async def get_prefix(bot, message):
    prefix = 'p,'

    if not message.guild:
        return commands.when_mentioned_or(*prefix)(bot, message)

    else:
        if message.guild.id in bot.prefixes:
            return commands.when_mentioned_or(bot.prefixes[message.guild.id])(bot, message)
        elif not message.guild.id in bot.prefixes:
            return commands.when_mentioned_or(*prefix)(bot, message)

config = configparser.ConfigParser()
config.read('config.ini')

activity=discord.Activity(type=discord.ActivityType.listening, name="@Penguin")


bot = PenguinBot(description='', 
                intents = intents, 
                allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False, replied_user = False), 
                embed_color = 0x31A1F1,
                activity = activity)

@bot.check
async def blacklisted(ctx):
    return ctx.author.id not in bot.blacklistedUsers

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    bot.translator = Translator()
    bot.welcome_dict = dict(await bot.db.fetch("SELECT guild_id, channel_id FROM welcome"))
    bot.dagpi_client = Client(config['default']['dagpi'])
    
if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.reply(embed = discord.Embed(title = str(error), color = discord.Color.red()))
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(embed = discord.Embed(title = str(error), color = discord.Color.red()))
    elif isinstance(error, commands.BadArgument):
        await ctx.reply(embed = discord.Embed(title = str(error), color = discord.Color.red()))
    elif isinstance(error, commands.NotOwner):
        await ctx.reply(embed = discord.Embed(title = "You are not an owner.", color = discord.Color.red()))
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.reply(embed = discord.Embed(description = str(error)))
    elif isinstance(error, discord.NotFound): await ctx.reply(embed = discord.Embed(description = str(error)))
    elif isinstance(error, commands.CommandOnCooldown): await ctx.reply(embed = discord.Embed(description = str(error)))
    elif isinstance(error, commands.CheckFailure): await ctx.reply(embed = discord.Embed(description = "You are blacklisted! Contact the owner to talk about it."))
    else:
        c = bot.get_channel(770685546724982845) 
        embed = discord.Embed(
            title = "An error occurred!",
            description = f"Reported to the support server. Need more help? [Join the support server](https://penguin.vaskel.xyz/support)\n```Error: \n{str(error)}```",
            timestamp = datetime.datetime.utcnow()
        )
        embed.set_footer(text = f"Caused by: {ctx.command}")
        await ctx.reply(embed = embed)
        
        #Support server embed
        embed = discord.Embed(
            title = f"An error occured!",
            description = f"```{str(error)}```",
            timestamp = datetime.datetime.utcnow()
        )
        embed.add_field(
            name = "Details:",
            value = f"""
            Caused by: `{str(ctx.author)} [{int(ctx.author)}]`
            In guild: `{str(ctx.guild)} [{int(ctx.guild)}]`
            Command: `{ctx.command}`
            """
        )
        await c.send(embed = embed)


botSecret = config['default']['BOT_SECRET']
bot.nasa_api = config['default']['NASA_API']
bot.run(botSecret, bot = True)