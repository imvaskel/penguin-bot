from discord.ext import commands


class ListenerCog(commands.Cog, name="Listener"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content in (f"<@!{self.bot.user.id}>", f"<@{self.bot.user.id}>"):
            ctx = await self.bot.get_context(message)
            cmd = self.bot.get_command("prefixes")

            await cmd(ctx)

    # Credit to https://github.com/platform-discord/travis-bott, license things, lol
    @commands.Cog.listener('on_message_edit')
    async def reinvoke_on_edit(self, before, after):
        if before.content != after.content:
            ctx = await self.bot.get_context(after)
            await self.bot.invoke(ctx)

    @commands.Cog.listener('on_command')
    async def on_command(self, ctx):
        try:
            self.bot.command_stats[ctx.command.name] += 1
        except KeyError:
            self.bot.command_stats[ctx.command.name] = 1


def setup(bot):
    bot.add_cog(ListenerCog(bot))
