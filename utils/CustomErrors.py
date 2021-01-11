from discord.ext import commands

class Blacklisted(commands.CommandError):
    """User is blacklisted"""
    pass
