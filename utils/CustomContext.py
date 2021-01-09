import discord
from discord.ext import commands

class PenguinContext(commands.Context):

    @property
    def test(self):
        return "hi"