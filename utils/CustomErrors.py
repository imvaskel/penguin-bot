from discord.ext import commands

class Blacklisted(commands.CheckFailure):
    """User is blacklisted"""
    pass
