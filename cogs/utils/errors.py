import discord
from discord.ext import commands
from discord.ext.commands import Cog
import datetime
import prettify_exceptions

class ErrorHandler(Cog, name = "Errors"):
    def __init__(self, bot):
        self.bot = bot
        
    @Cog.listener()
    async def on_command_error(self, ctx, error):
        ignored_errors = (commands.CommandNotFound)
        
        error = getattr(error, "original", error)

        if isinstance(error, ignored_errors):
            return

        setattr(ctx, "original_author_id", getattr(ctx, "original_author_id", ctx.author.id))
        owner_reinvoke_errors = (
            commands.CommandOnCooldown, commands.DisabledCommand
        )

        if ctx.original_author_id in self.bot.owner_ids and isinstance(error, owner_reinvoke_errors):
            return await ctx.reinvoke()
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, (commands.MissingPermissions, commands.MissingRequiredArgument, commands.BadArgument, commands.BotMissingPermissions,
                                discord.NotFound, commands.CommandOnCooldown, commands.BadUnionArgument)):
            await ctx.reply(embed = discord.Embed(title = str(error), color = discord.Color.red()))
        elif isinstance(error, commands.NotOwner):
            await ctx.reply(embed=discord.Embed(title="You do not own this bot.", color=discord.Color.red()))
        else:
            c = self.bot.get_channel(770685546724982845)
            prettify_exceptions.DefaultFormatter().theme['_ansi_enabled'] = False
            traceback = ''.join(prettify_exceptions.DefaultFormatter().format_exception(type(error), error, error.__traceback__))
            embed = discord.Embed(
                title = "An error occurred!",
                description = f"Reported to the support server. Need more help? [Join the support server](https://penguin.vaskel.xyz/support)\n```Error: \n{traceback}```",
                timestamp = datetime.datetime.utcnow()
            )
            embed.set_footer(text = f"Caused by: {ctx.command}")
            await ctx.reply(embed = embed)

            #Support server embed
            embed = discord.Embed(
                title = f"An error occurred!",
                description = f"```{traceback}```",
                timestamp = datetime.datetime.utcnow()
            )
            embed.add_field(
                name = "Details:",
                value = f"""
                Caused by: `{str(ctx.author)} [{int(ctx.author)}]`
                In guild: `{str(ctx.guild)} [{int(ctx.guild)}]`
                Command: `{ctx.command}`
                """
            )
            await c.send(embed = embed)

def setup(bot):
    bot.add_cog(ErrorHandler(bot))
