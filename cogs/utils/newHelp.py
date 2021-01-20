import discord
from discord.ext import commands, menus
from listeners.errors import ErrorEmbed

class CogHelpSource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=6)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        embed = discord.Embed(title=entries[0].cog_name)

        for i, v in enumerate(entries, start=offset):
            command = v.formatted
            embed.add_field(name = command[0],
                            value = command[1],
                            inline=False)
        return embed

class CogHelpPages(menus.MenuPages):
    def __init__(self, source):
        super().__init__(source, delete_message_after=True)

class PenguinHelp(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={
            "cooldown": commands.Cooldown(1, 5, commands.BucketType.member),
            "help": "The help command"
        })

    async def command_not_found(self, string):
        channel = self.get_destination()
        await channel.send(embed=discord.Embed(description=f"The command `{string}` was not found."))

    async def send_bot_help(self, mapping):
        filtered_commands = {key: await self.filter_commands(value) for key, value in mapping.items() if getattr(key, "qualified_name", "None") != "IpcRoutes"}
        embed = discord.Embed(title = "Help",
                              description=f"Use `{self.clean_prefix}help` [command] or [module] for more help.")
        for cog, cmds in filtered_commands.items():
            if cmds:
                embed.add_field(name = getattr(cog, "qualified_name", "None"),
                                value =f"{' '.join([f'`{command.name}`' for command in cmds])}",
                                inline=False)
        await self.get_destination().send(embed = embed)
    
    async def send_cog_help(self, cog):
        menu = CogHelpPages(source=CogHelpSource([FormatCogHelp(command) for command in cog.get_commands()]))
        await menu.start(self.context)

    async def send_command_help(self, command):
        embed = discord.Embed(title= command.qualified_name,
                              description = ("`<arg>` This is a required arg \n"
                                             "`[arg]` This is optional \n"
                                             "`[arg...]` This can have multiple args"))
        command = (await self.filter_commands([command]))

        if not command:
            return await self.get_destination().send(embed = embed)

        embed.add_field(name="Help",
                        value = command.help or "None",
                        inline=False)
        embed.add_field(name="Aliases",
                        value = "\n".join([f"`{alias}`" for alias in command.aliases]) or "None",
                        inline=False)
        embed.add_field(name="Args",
                        value= command.signature or "None",
                        inline=False)
        await self.get_destination().send(embed = embed)
