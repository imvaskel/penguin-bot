import discord
from discord.ext import commands
from datetime import datetime

class PenguinContext(commands.Context):

    async def embed(self, *args, **kwargs):
        """Sends an embed with the args given"""
        embed = discord.Embed(**kwargs, color=0x36393E, timestamp=datetime.utcnow())
        embed.set_footer(icon_url=str(self.author.avatar_url), text=f"Requested by {self.author}")
        await self.send(embed = embed)

    async def refresh_cache(self):
        """Refreshes the cache for the guild in the ctx object"""
        self.bot.cache.update(self.bot.refresh_template(await self.bot.db.fetchrow("SELECT * FROM guild_config WHERE id = $1", self.guild.id)))

    async def codeblock(self, text):
        """Makes the given text into a code block"""
        if len(text) > 2042: 
            return await self.send("Given text is too long")
        return await self.send("```" + text + "```")
