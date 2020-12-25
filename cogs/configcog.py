import discord
from discord.ext import commands
from listeners.errors import ErrorEmbed

class ConfigCog(commands.Cog, name = "config"):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.manage_guild

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply(embed = ErrorEmbed(description="You don't have the `mange guilds permission`"))
        else:
            raise error

    @commands.command()
    async def test(self, ctx):
        raise ValueError("Test")

    @commands.command()
    async def test2(self, ctx):
        await ctx.reply("test")

def setup(bot):
    bot.add_cog(ConfigCog(bot))
