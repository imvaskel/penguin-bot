import discord
from discord.ext import commands
from listeners.errors import ErrorEmbed

class PenguinHelp(commands.HelpCommand):
    async def command_not_found(self, string):
        channel = self.get_destination()
        await channel.send(embed=discord.Embed(description=string))

    async def send_bot_help(self, mapping):
        filtered_commands = {key: await self.filter_commands(value) for key, value in mapping.items() if getattr(key, "qualified_name", "None") != "IpcRoutes"}
        embed = discord.Embed(title = "Help",
                              description=f"Use `{self.clean_prefix}` help [command] or [module] for more help.")
        for cog, cmds in filtered_commands.items():
            embed.add_field(name = getattr(cog, "qualified_name", "None"),
                            value = "\n".join([
                                f"`{command.name}`" for command in cmds]))
        await self.get_destination().send(embed = embed)
