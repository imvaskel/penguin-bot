import discord
from discord.ext import commands, menus
from listeners.errors import ErrorEmbed

class FormatCogHelp:
    def __init__(self, command):
        newline = "\n"
        self.formatted = command.name
        if command.aliases:
           self.formatted += f"[{' | '.join([alias for alias in command.aliases])}]"
        self.formatted += "\nNone" if not command.help else "\n" + command.help
        

class CogHelpSource(menus.ListPageSource):
    def __init__(self):
        super().__init__(source, per_page=6)

    async def format_page(self, menu, commands):
        newline = "\n"
        embed = discord.Embed(title = cog.qualified_name,
        description= newline.join([command.formatted for command in commands]))
        
        embed.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()}")
        return embed

class CogHelpPages(menus.MenuPages):
    def __init__(self, source):
        super().__init__(source, delete_message_after=True)         

class PenguinHelp(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={
            "cooldown" : commands.Cooldown(1, 5, commands.BucketType.member),
            "help" : "The help command"
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
        menu = CogHelpPages(CogHelpSource([FormatCogHelp(command) for command in cog.get_commands()]))
        await menu.start(self.context)
