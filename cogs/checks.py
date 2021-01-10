import discord
from discord.ext import commands
from utils.CustomErrors import *
from utils.CustomBot import PenguinBot
from listeners.errors import ErrorEmbed

class CheckCog(commands.Cog):
    def __init__(self, bot: PenguinBot):
        self.bot = bot
        bot.add_check(self.isBlacklisted)

    async def cog_command_error(self, ctx, error):
        error = getattr(error, 'original', error)
        if isinstance(error, Blacklisted):
            await ctx.reply(embed=ErrorEmbed(description=str(error)))


    async def isBlacklisted(self, ctx):
        if ctx.author.id in self.bot.blacklistedUsers:
            raise Blacklisted("You are blacklisted!")
        return True

def setup(bot):
    bot.add_cog(CheckCog(bot))
