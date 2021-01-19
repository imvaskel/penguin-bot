import discord
from discord.ext import commands
from listeners.errors import ErrorEmbed

class PenguinHelp(commands.HelpCommand):
    async def command_not_found(self, string):
        channel = self.get_destination()
        return await channel.send(embed=discord.Embed(description=string))