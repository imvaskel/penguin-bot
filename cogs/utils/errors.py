import discord
from discord.ext import commands
from datetime import datetime

class ErrorsCog(commands.Cog, name = "Errors"):
    """Errors stuff"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener('on_command_error')
    async def command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.reply(embed=discord.Embed(description=str(error), color=discord.Color.red()))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(embed=discord.Embed(description=str(error), color=discord.Color.red()))
        elif isinstance(error, commands.BadArgument):
            await ctx.reply(embed=discord.Embed(description=str(error), color=discord.Color.red()))
        elif isinstance(error, commands.NotOwner):
            await ctx.reply(embed=discord.Embed(description="You are not an owner.", color=discord.Color.red()))
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.reply(embed=discord.Embed(description=str(error)))
        elif isinstance(error, discord.NotFound):
            await ctx.reply(embed=discord.Embed(description=str(error)))
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(embed=discord.Embed(description=str(error)))
        elif isinstance(error, commands.CheckFailure):
            await ctx.reply(embed=discord.Embed(description="You are blacklisted! Contact the owner to talk about it."))
        else:
            c = self.bot.get_channel(770685546724982845)
            embed = discord.Embed(
                title="An error occurred!",
                description=f"Reported to the support server. Need more help? [Join the support server](https://penguin.vaskel.xyz/support)\n```Error: \n{str(error)}```",
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(text=f"Caused by: {ctx.command}")
            await ctx.reply(embed=embed)

            # Support server embed
            embed = discord.Embed(
                title=f"An error occurred!",
                description=f"```{str(error)}```",
                timestamp= datetime.utcnow()
            )
            embed.add_field(
                name="Details:",
                value=f"""
                Caused by: `{str(ctx.author)} [{int(ctx.author)}]`
                In guild: `{str(ctx.guild)} [{int(ctx.guild)}]`
                Command: `{ctx.command}`
                """
            )
            await c.send(embed=embed)

def setup(bot):
    bot.add_cog(ErrorsCog(bot))