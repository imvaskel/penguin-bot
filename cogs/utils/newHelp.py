import discord
from discord.ext import commands
from listeners.errors import ErrorEmbed

class PenguinHelp(commands.HelpCommand):
    def command_not_found(self, string):
        return discord.Embed(description=string)