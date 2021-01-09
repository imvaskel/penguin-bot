import discord
from discord.ext import commands
from datetime import datetime

class PenguinContext(commands.Context):

    async def embed(self, *args, **kwargs):
        """Sends an embed with the args given"""
        embed = discord.Embed(**kwargs, color=0x36393E, timestamp=datetime.utcnow())
        embed.set_footer(icon_url=str(self.author.avatar_url), text=f"Requested by {self.author}")
        await self.send(embed = embed)

