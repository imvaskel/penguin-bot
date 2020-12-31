import discord
from discord.ext import commands, ipc
from utils.CustomBot import PenguinBot


class IpcRoutes(commands.Cog):
    def __init__(self, bot: PenguinBot):
        self.bot = bot

    @ipc.server.route()
    async def get_member_count(self, data):
        guild = int(data.guild_id)  # get the guild object using parsed guild_id

        await self.bot.refresh_cache_for(guild)


def setup(bot):
    bot.add_cog(IpcRoutes(bot))