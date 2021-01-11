import discord
from discord.ext import commands, ipc
import os
import configparser
import mystbin
from asyncdagpi import Client
from utils.CustomBot import PenguinBot
from utils.CustomErrors import *

startup_extensions = ['cogs.members', 'cogs.owner', 'cogs.moderator', 'cogs.fun', "jishaku", "cogs.mute",
                      'cogs.animals', 'listeners.listener', 'cogs.help_command', 'cogs.images',
                      'cogs.settings', 'cogs.checks',
                      'listeners.errors', 'listeners.guilds', 'listeners.moderation',
                      'listeners.reactionroles', 'listeners.welcomer']

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_HIDE"] = "True"

intents = discord.Intents.default()
intents.members = True

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

@bot.event
async def on_ready():
    print(
        "Logged in! \n"
        f"{'-' * 20}\n"
        f"Bot Name: {bot.user} \n"
        f"Bot ID: {bot.user.id} \n"
        f"{'-' * 20}"
    )

bot.mystbin = mystbin.Client()


@bot.event
async def on_error(event, *args, **kwargs):
    ignored_events = ["on_member_join", "on_message", "on_raw_reaction_add"]
    if event in ignored_events:
        return
    else:
        raise

if __name__ == "__main__":
    botSecret = config['default']['BOT_SECRET']
    bot.ipc.start()
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))
    bot.run(botSecret)
