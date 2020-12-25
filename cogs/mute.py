"""
Updated for discord.py 1.0.x / Rewrite
Original credit goes to Vexs
"""

import discord
import asyncio
import re
from discord.ext import commands
import sys
import traceback
import aiosqlite


time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k]*float(v)
            except KeyError:
                raise commands.BadArgument(
                    "{} is an invalid time-key! h/m/s/d are valid!".format(k))
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))
        return time


class MuteCog(commands.Cog, name="Mute"):
    """Commands for muting, I should move this"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, time: TimeConverter = None):
        """Mutes a member for the specified time- time in 2d 10h 3m 2s format ex:
        mute @Someone 1d"""
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            return await ctx.send("The muted role doesn't exist, run `mute_setup` to make another.")
        if role > ctx.me.top_role:
            return await ctx.send("The muted role is above mine!")
        if role in member.roles:
            return await ctx.send("This user already has the muted role!")
        if role > ctx.author.top_role:
            return await ctx.send("Your role is not above the Muted role!")
        await member.add_roles(role)
        await ctx.send(("Muted {} for {}s" if time else "Muted {}").format(member, time))
        if time:
            await asyncio.sleep(time)
            await member.remove_roles(role)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            return await ctx.send("The muted role doesn't exist, run `mute_setup` to make another.")
        if role not in member.roles:
            return await ctx.send("This user doesn't have the muted role!")
        if role > ctx.me.top_role:
            return await ctx.send("The muted role is above mine!")
        if role > ctx.author.top_role:
            return await ctx.send("Your role is not above the Muted role!")
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("The member's top role is above yours!")
        await member.remove_roles(role)
        await ctx.send(f"Unmuted {str(member)}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute_setup(self, ctx):
        """Sets up muting role for muting"""
        l1 = ""
        l2 = ""
        guild = ctx.guild
        if "Muted" not in guild.roles:
            await guild.create_role(name="Muted", reason="Automatically created for muting.", permissions=discord.Permissions(send_messages=False))
        mutedRole = discord.utils.get(guild.roles, name="Muted")
        if mutedRole > ctx.me.top_role:
            return await ctx.send("The muted role is above mine!")
        for channel in guild.text_channels:
            perms = channel.overwrites_for(mutedRole)
            try:
                await channel.set_permissions(mutedRole, send_messages=False)
                l1 += f"{channel} "
            except discord.HTTPException:
                l2 += f"{channel} "
                pass
        embed = discord.Embed()
        embed.add_field(name="Successful: ", value=l1)
        embed.add_field(name="Unsuccessful: ", value=l2)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(MuteCog(bot))
