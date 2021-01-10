import discord
from discord.ext import commands
from utils.CustomErrors import *

class CheckCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.bot_check()
    async def isBlacklisted(self, ctx):
        if ctx.author.id in self.bot.blacklistedUsers:
            raise Blacklisted("You are blacklisted!")
        return True

def setup(bot):
    bot.add_cog(CheckCog(bot))
