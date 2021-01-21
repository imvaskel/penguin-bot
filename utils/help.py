import discord
from discord.ext import commands, menus

class FormatCogHelp:
    def __init__(self, command: commands.Command):
        formatted = f"[{' | '.join([alias for alias in command.aliases])}]" if command.aliases else ""
        formatted += "\nNone" if not command.help else "\n" + command.help
        self.formatted = (command.name, formatted)
        self.cog_name = command.cog_name

class GroupHelpSource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=5)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        embed = discord.Embed(title = entries[0].root_parent.qualified_name,
                              color=0x36393E)

        for index, command in enumerate(entries, start=offset):
            embed.add_field(name=command.qualified_name,
                            value=(
                                f"[{' | '.join([alias for alias in command.aliases])}] \n" if command.aliases else ""
                                f"{command.help or 'None'}"
                            ))
        return embed

class CogHelpSource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=6)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        embed = discord.Embed(title=entries[0].cog_name,
                              color= 0x36393E)

        for i, v in enumerate(entries, start=offset):
            command = v.formatted
            embed.add_field(name = command[0],
                            value = command[1],
                            inline=False)
        embed.set_footer(text = f"Page {menu.current_page+1} / {self.get_max_pages()}")
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
        return f"The command `{string}` was not found."

    async def send_bot_help(self, mapping):
        filtered_commands = {key: await self.filter_commands(value) for key, value in mapping.items() if getattr(key, "qualified_name", "None") != "IpcRoutes"}
        embed = discord.Embed(title = "Help",
                              description=f"Use `{self.clean_prefix}help` [command] or [module] for more help.",
                              color=0x36393E)
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
                                             "`[arg...]` This can have multiple args"),
                              color=0x36393E)
        command = (await self.filter_commands([command]))[0]

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

    async def send_group_help(self, group: commands.Group):
        menu = CogHelpPages(source=GroupHelpSource([command for command in group.commands]))
        await menu.start(self.context)
