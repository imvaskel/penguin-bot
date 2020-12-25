import discord
from discord.ext import commands
import os
import configparser
import mystbin
from aiogoogletrans import Translator
from asyncdagpi import Client
from utils.CustomBot import PenguinBot

startup_extensions = ['cogs.members', 'cogs.owner', 'cogs.moderator', 'cogs.fun', "jishaku", "cogs.mute",
                      'cogs.animals', 'listeners.listener', 'cogs.help_command', 'cogs.images',
                      'listeners.errors', 'listeners.guilds', 'listeners.moderation',
                      'listeners.reactionroles', 'listeners.welcomer']

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_HIDE"] = "True"

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

activity = discord.Activity(
    type=discord.ActivityType.listening, name="@Penguin")


bot = PenguinBot(description='',
                 intents=intents,
                 allowed_mentions=discord.AllowedMentions(
                     roles=False, users=True, everyone=False, replied_user=False),
                 embed_color=0x31A1F1,
                 activity=activity,
                 owner_ids={447422100798570496})


@bot.check
async def blacklisted(ctx):
    return ctx.author.id not in bot.blacklistedUsers


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    bot.translator = Translator()
    bot.welcome_dict = dict(await bot.db.fetch("SELECT guild_id, channel_id FROM welcome"))
    bot.dagpi_client = Client(config['default']['dagpi'])

bot.mystbin = mystbin.Client()


@bot.event
async def on_error(event, *args, **kwargs):
    ignored_events = ["on_member_join", "on_message", "on_raw_reaction_add"]
    if event in ignored_events:
        return
    else:
        raise

if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

botSecret = config['default']['BOT_SECRET']
bot.nasa_api = config['default']['NASA_API']
bot.run(botSecret, bot=True)
