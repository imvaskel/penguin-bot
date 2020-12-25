import discord
from discord.ext import commands
from discord.ext.commands import Cog
import datetime
import prettify_exceptions
from datetime import datetime


class ErrorEmbed(discord.Embed):
    def __init__(self, description, **kwargs):
        super().__init__(color=discord.Color.red(),
                         title="An error occurred!",
                         description=description,
                         timestamp=datetime.utcnow())


class ErrorHandler(Cog, name="Errors"):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        ignored_errors = (commands.CommandNotFound)
        stringed_errors = (commands.MissingPermissions, commands.MissingRequiredArgument, commands.BadArgument,
                           commands.BotMissingPermissions,
                           discord.NotFound, commands.CommandOnCooldown, commands.BadUnionArgument)

        error = getattr(error, "original", error)

        if isinstance(error, ignored_errors):
            return

        setattr(ctx, "original_author_id", getattr(
            ctx, "original_author_id", ctx.author.id))
        owner_reinvoke_errors = (
            commands.CommandOnCooldown, commands.DisabledCommand
        )

        if ctx.original_author_id in self.bot.owner_ids and isinstance(error, owner_reinvoke_errors):
            return await ctx.reinvoke()
        if isinstance(error, stringed_errors):
            await ctx.reply(embed=ErrorEmbed(description=str(error)))
        elif isinstance(error, commands.NotOwner):
            await ctx.reply(embed=ErrorEmbed(description="You do not own this bot."))
        elif isinstance(error, commands.CheckFailure):
            await ctx.reply(embed=ErrorEmbed(description="You are blacklisted, join the support server to find out more https://penguin.vaskel.xyz/support"))

        else:
            c = self.bot.get_channel(770685546724982845)
            prettify_exceptions.DefaultFormatter(
            ).theme['_ansi_enabled'] = False
            traceback = ''.join(prettify_exceptions.DefaultFormatter(
            ).format_exception(type(error), error, error.__traceback__))
            embed = ErrorEmbed(
                description=f"Reported to the support server. Need more help? [Join the support server](https://penguin.vaskel.xyz/support)\n```Error: \n{traceback}```",
            )
            embed.set_footer(text=f"Caused by: {ctx.command}")
            await ctx.reply(embed=embed)

            # Support server embed
            embed = ErrorEmbed(
                description=f"```{traceback}```",
            )
            embed.add_field(
                name="Details:",
                value=f"""
                Caused by: `{str(ctx.author)} [{ctx.author}.id]`
                In guild: `{str(ctx.guild)} [{ctx.guild.id}]`
                Command: `{ctx.command}`
                """
            )
            await c.send(embed=embed)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
