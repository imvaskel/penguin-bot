import discord
from discord.ext import commands
from utils.CustomBot import PenguinBot
from contextlib import suppress

def hierarchy_check(ctx, member):
    """A check for hierarchy for the bot, the author, etc."""

class ModeratorCog(commands.Cog, name="Moderator"):
    """Commands for moderators"""

    def __init__(self, bot: PenguinBot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kicks a user, you can use `Username` `Username#discriminator` or `userId`"""
        if member.id == ctx.author.id:
            return await ctx.send("You can't do that to yourself!")
        if member.top_role > ctx.me.top_role or member.top_role == ctx.me.top_role:
            return await ctx.send("That member's top role is higher or equal to mine!")
        try:
            await member.send(f"You were kicked from {ctx.guild.name} for {reason}")
        except discord.HTTPException:
            pass
        await member.kick(reason=reason)
        await ctx.send(f"Kicked {member.name} for {reason}")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Bans a user, you can use `Username` `Username#discriminator` or `userId`"""
        if member.id == ctx.author.id:
            return await ctx.send("You can't do that to yourself!")
        if member.top_role >= ctx.me.top_role:
            return await ctx.send("That member's top role is higher or equal to mine!")

        guild = ctx.guild

        with suppress(discord.HTTPException):
            await member.send(f"You were banned from {guild.name} for {reason}")

        reason = f"{ctx.author} [{ctx.author.id}] - {reason}"
        await guild.ban(member, reason=reason)
        await ctx.send(f"{member.name} was banned for {reason}.")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user: int, *, reason=None):
        """Unbans a user with a given ID"""
        if user == ctx.author.id:
            return await ctx.send("You can't do that to yourself!")
        member = discord.Object(id=user)
        try:
            await ctx.guild.unban(member, reason=f"{ctx.author} [{ctx.author.id}] - {reason}")
            await ctx.send(embed=discord.Embed(description=f"Unbanned {member.id} for {reason}."))
        except discord.NotFound:
            return await ctx.send(embed=discord.Embed(description="That user doesn't seem to be banned."))

    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.command(help="Clears X messages up to 500, also can do only Y member's messages")
    async def clear(self, ctx, num: int, target: discord.Member = None):
        if num > 500 or num < 0:
            return await ctx.send("Invalid amount. Maximum is 500.")

        def msgcheck(amsg):
            if target:
                return amsg.author.id == target.id
            return True
        deleted = await ctx.channel.purge(limit=num, check=msgcheck)
        await ctx.send(f':thumbsup: Deleted **{len(deleted)}/{num}** possible messages for you.', delete_after=10)

    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    @commands.command()
    async def block(self, ctx, user: discord.Member):
        """Blocks a user from sending messages in the channel"""
        if user == ctx.author.id:
            return await ctx.send("You can't do that to yourself!")
        if user.top_role >= ctx.me.top_role:
            return await ctx.send("That member's top role is higher or equal to mine!")
        if user.top_role >= ctx.me.top_role:
            return await ctx.send("That member's top role is higher or equal to yours!")
        channel = ctx.channel

        await channel.set_permissions(user, send_messages=False)
        await ctx.send(f"{user} was blocked from the channel.")

    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    @commands.command()
    async def unblock(self, ctx, user: discord.Member):
        """Unblocks the given user from the channel:"""
        if user.top_role > ctx.me.top_role or user.top_role == ctx.me.top_role:
            return await ctx.send("That member's top role is higher or equal to mine!")
        if user.top_role > ctx.author.top_role or user.top_role == ctx.author.top_role:
            return await ctx.send("That member's top role is higher or equal to yours!")
        channel = ctx.channel

        await channel.set_permissions(user, send_messages=True)
        await ctx.send(f"{user} was unblocked from the channel.")

    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.guild_only()
    @commands.command(help="Adds a slowmode to a channel in seconds, use no arg or 0 to remove slowmode.")
    async def slowmode(self, ctx, seconds: int = None):
        channel = ctx.channel

        if not seconds:
            await channel.edit(slowmode_delay=0)

        await channel.edit(slowmode_delay=seconds)

    @commands.has_permissions(manage_guild=True)
    @commands.command(description="Leaves guild, only usable by users with the `manage_guild` permission.")
    async def leave(self, ctx):
        await ctx.send(f"Leaving server {ctx.guild.name}, goodbye.")
        print(f"Left server {ctx.guild.name}")
        await ctx.guild.leave()

    @commands.command(description="This bans a user, but saves their messages.")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def saveban(self, ctx, member: discord.Member, *, reason=None):
        if member.id == ctx.author.id:
            return await ctx.send("You can't do that to yourself!")

        if member.top_role >= ctx.me.top_role:
            return await ctx.send("That member's top role is higher or equal to mine!")

        guild = ctx.guild
        audit = f"{ctx.author} [{ctx.author.id}] - {reason}"
        try:
            await member.send(
                embed=discord.Embed(
                    description=f"You were banned from {guild.name} for {audit}")
            )
        except discord.HTTPException:
            pass
        await guild.ban(member, delete_message_days=0, reason=audit)
        await ctx.send(f"{member.name} was banned for {audit}.")


def setup(bot):
    bot.add_cog(ModeratorCog(bot))
