import discord
from discord.ext import commands

class PenguinContext(commands.Context):

    @property
    async def embed(self, *args, **kwargs):
        """Sends an embed with the args given"""
        embed = discord.Embed(**kwargs)
        await self.send(embed = embed)

