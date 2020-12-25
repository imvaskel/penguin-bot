import discord
from discord.ext import commands


class GuildsListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.limit = 0.70

    @commands.Cog.listener('on_guild_join')
    async def botfarm(self, guild):
        botPercent = sum(m.bot for m in guild.members) / guild.member_count
        if botPercent >= self.limit:
            try:
                await guild.owner.send(f"It seems your guild has over {self.limit * 100}% bot to user ratio, it has automatically left. If you think this is an error, please join the support server at https://penguin.vaskel.xyz/support and ask in #help.")
            except:
                pass
            await guild.leave()


def setup(bot):
    bot.add_cog(GuildsListener(bot))
