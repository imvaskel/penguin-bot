import discord
from discord.ext import commands, ipc
from utils.CustomBot import PenguinBot
import json

def template(name, help, arguments, aliases):
            return {"command": name, "help": help, "arguments": arguments, "aliases": aliases}

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
        l = []

        for command in self.bot.commands:
            if command.cog_name == "Owner":
                continue
            l.append(template(command.name, command.help or 'None', command.signature if command.signature != "," else 'None', command.aliases or 'None'))
        l = json.dumps(l)
        return l



def setup(bot):
    bot.add_cog(IpcRoutes(bot))