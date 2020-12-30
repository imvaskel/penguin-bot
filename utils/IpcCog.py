import discord
from discord.ext import commands, ipc
from utils.CustomBot import PenguinBot


class IpcCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ipc.Server.route()
    async def refresh_cache_for_guild(self, data):
        try:
            await self.bot.refresh_cache_for(data.guildId)
            return "Successful"
        except Exception as e:
            return "Error"

def setup(bot):
    bot.add_cog(IpcCog(bot))
