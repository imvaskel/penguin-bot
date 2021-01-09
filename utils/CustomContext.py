import discord
from discord.ext import commands
from datetime import datetime

class PenguinContext(commands.Context):

    async def embed(self, *args, **kwargs):
        """Sends an embed with the args given"""
        embed = discord.Embed(**kwargs, timestamp=kwargs.get("timestamp") or datetime.utcnow())
        embed.set_footer(text=f"Requested by {self.author}")
        await self.send(embed = embed)

