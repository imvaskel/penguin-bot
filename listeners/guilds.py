import discord
import datetime
from discord.ext import commands
from contextlib import suppress
import asyncpg


class GuildsListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.limit = 0.70

    @commands.Cog.listener('on_guild_join')
    async def botfarm(self, guild):
        botPercent = sum(m.bot for m in guild.members) / guild.member_count
        if botPercent >= self.limit:
            try:
                await guild.owner.send(f"It seems your guild has over {self.limit * 100}% bot to user ratio, it has automatically left.\n"
                                       "If you think this is an error, please join the support server at https://penguin.vaskel.xyz/support and ask in #help.")
            except:
                pass
            await guild.leave()

    @commands.Cog.listener('on_guild_remove')
    async def on_guild_leave(self, guild):

        with suppress(Exception):
            await self.bot.db.execute("DELETE FROM guild_config WHERE id = $1", guild.id)

        c = self.bot.get_channel(781615213421658142)

        # Guild information sent to this channel
        embed = discord.Embed(
            title="Guild Left!",
            description=("```yaml\n"
                         f"Guild Name - {guild}\n"
                         f"Guild ID - {guild.id}\n"
                         f"Guild Owner - {guild.owner} [{guild.owner.id}]\n"
                         f"Guild Created - {guild.created_at.strftime('%b %d, %Y %I:%M %p')}\n"
                         f"Guild Members - {len(guild.members)}\n"
                         "```"
                         ),
            timestamp=datetime.datetime.utcnow()
        )
        await c.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):

        await self.bot.db.execute(f"INSERT INTO guild_config(id) VALUES ($1) ON CONFLICT DO NOTHING", guild.id)

        p = await self.bot.db.fetchrow("SELECT id, prefix FROM guild_config WHERE id = $1", guild.id)

        self.bot.prefixes[guild.id] = p['prefix']

        record = await self.bot.db.fetchrow("SELECT * FROM guild_config WHERE id = $1", guild.id)

        d = self.bot.refresh_template(record)

        self.bot.cache.update(d)
        print(f"I have joined {guild.name} [{guild.id}]")

        c = self.bot.get_channel(781615213421658142)
        # Guild information sent to this channel
        embed = discord.Embed(
            title="Guild Joined!",
            description=("```yaml\n"
                         f"Guild Name - {guild}\n"
                         f"Guild ID - {guild.id}\n"
                         f"Guild Owner - {guild.owner} [{guild.owner.id}]\n"
                         f"Guild Created - {guild.created_at.strftime('%b %d, %Y %I:%M %p')}\n"
                         f"Guild Members - {len(guild.members)}\n"
                         "```"
                         ),
            timestamp=datetime.datetime.utcnow()
        )
        await c.send(embed=embed)


def setup(bot):
    bot.add_cog(GuildsListener(bot))
