from discord.ext import commands, menus
from utils.help import PenguinHelp

class HelpCog(commands.Cog, name="Help"):
    def __init__(self, bot):
        self.bot = bot
        bot.help_command = PenguinHelp()
        bot.help_command.cog = self


def setup(bot):
    bot.add_cog(HelpCog(bot))
