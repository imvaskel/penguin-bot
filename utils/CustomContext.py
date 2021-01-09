import discord
from discord.ext import commands

class PenguinContext(commands.Context):

    @property
    async def test(self):
        return "hi"