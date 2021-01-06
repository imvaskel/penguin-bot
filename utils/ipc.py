import discord
from discord.ext import commands, ipc
from utils.CustomBot import PenguinBot
import json

def template(command: commands.Command):
            return {"command": command.name,
                    "help": command.help or "None",
                    "arguments": command.signature or "None",
                    "aliases": " ".join(command.aliases) or "None"}

class IpcRoutes(commands.Cog):
    def __init__(self, bot: PenguinBot):
        self.bot = bot

    @ipc.server.route()
    async def refresh_cache_for_guild(self, data):
        guild = data.guild_id
        guild = int(guild)

        try:
            await self.bot.refresh_cache_for(guild)
            return "done"
        except Exception as e:
            print(e)
            return "error"

    @ipc.server.route()
    async def get_guild_ids(self):
        return [i.id for i in self.bot.guilds]

    @ipc.server.route()
    async def get_help_commands(self):
        l = [template(command) for command in self.bot.commands]
        return {"data": l}




def setup(bot):
    bot.add_cog(IpcRoutes(bot))