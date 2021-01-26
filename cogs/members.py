import base64
from re import L
from subprocess import call

import discord
import datetime
import re
import asyncio
import psutil
import json
import time
import platform
import inspect
import os
from discord.ext import commands, menus
import typing

class MembersCog(commands.Cog, name="Meta"):
    """Commands that give information about things"""

    def __init__(self, bot):
        self.bot = bot

        self.perms_emotes = [
            "<:redTick:775792645728895038>",
            "<:greentick:770685801297215488>"
        ]

    def _filter_perms(self, perms: discord.Permissions):
        ret = []

        # v = permission's (name, value)
        for filtered in filter(lambda v: v[1], perms):
            ret.append(filtered[0])
        return ret

    def _get_filtered_perms(self):
        permissions = (
            discord.Permissions.text(),
            discord.Permissions.voice(),
            discord.Permissions.general()
        )
        filtered = {
            "text": None,
            "voice": None,
            "general": None
        }

        for key, obj in zip(filtered.keys(), permissions):
            filtered[key] = self._filter_perms(obj)
        return filtered

    def _format_perm_name(self, name: str):
        name = name.title()
        replacements = (
            ("_", " "),
            ("Tts", "TTS")
        )

        for sub, repl in replacements:
            name = name.replace(sub, repl)
        return name

    @commands.command()
    @commands.guild_only()
    async def joined(self, ctx, *, member: discord.Member = None):
        """Displays when the user joined, not formatted though"""
        if not member:
            member = ctx.author
        await ctx.send(f'{member.display_name} joined on {member.joined_at}')

    @commands.command(name='perms', aliases=['perms_for', 'permissions'])
    @commands.guild_only()
    async def check_permissions(self, ctx, *, member: discord.Member = None):
        """Returns permissions"""
        member = member if member else ctx.author
        filtered = self._get_filtered_perms()
        types = {k: [] for k in filtered.keys()}
        embed = discord.Embed(title=f"Permissions for {member} in {ctx.guild}")

        for key, value in member.guild_permissions:
            for channel_type, names in filtered.items():
                if key in names:
                    name = self._format_perm_name(key)
                    emote = self.perms_emotes[value]
                    types[channel_type].append((name, emote))
                    break

        for key, perms in types.items():
            sorted_ = sorted(perms, key=lambda v: v[0])
            formatted = [f"{e} {n}" for n, e in sorted_]
            value = ("\n").join(formatted)

            embed.add_field(name=f"{key.title()} Permissions", value=value)
        await ctx.send(embed=embed)

    @commands.command(aliases=["about"])
    async def info(self, ctx):
        """Displays bot info"""
        botOwner = self.bot.get_user(list(self.bot.owner_ids)[0])
        mem = psutil.virtual_memory()
        embed = discord.Embed(title="Bot Info")
        embed.set_author(name=str(botOwner), icon_url=botOwner.avatar_url)
        embed.set_footer(text=self.bot.user, icon_url=self.bot.user.avatar_url)
        embed.add_field(name="About me",
                        value=f"Hello, I am a bot made by {str(botOwner)} in discord.py! \n[Support Server](https://penguin.vaskel.xyz/invite).")
        embed.add_field(
            name=f"Servers: {len(self.bot.guilds)}", value=f"Users: {len(self.bot.users)}")
        embed.add_field(name="Usage:",
                        value=f"```{mem[0] / 1000000} MB total \n{mem[1] / 1000000} MB available ({100 - mem[2]}%)```",
                        inline=False)
        embed.add_field(name="Version Info:",
                        value=f"```Python: {platform.python_version()} \nDiscord.py: {discord.__version__}```")
        embed.add_field(name="Vote me!",
                        value="[Top.GG](https://top.gg/bot/753037464599527485) \n[Discord Extreme List](https://discordextremelist.xyz/en-US/bots/penguin)")
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        """Returns the ping, in response time and ping to discord"""
        start = time.perf_counter()
        message = await ctx.send("Ping...")
        end = time.perf_counter()
        duration = round((end - start) * 1000)
        embed = discord.Embed(title="Ping",
                              description=f"\U0001f3d3 Pong!\n ```Bot Latency: {round(self.bot.latency * 1000)} ms \nResponse Time: {duration} ms```")
        await message.delete()
        await ctx.send(embed=embed)

    @commands.command(aliases=['whois'],
                      help="Returns information about a user, if left blank will return the author's info.")
    async def userinfo(self, ctx, user: typing.Union[discord.Member, discord.User] = None):
        user = user or ctx.author
        msgAuthor = ctx.author
        embed = discord.Embed()

        if isinstance(user, discord.Member):
            roles = ["None"] if len(user.roles) == 1 else [
                i.mention for i in user.roles if i.name != "@everyone"]
            roles = "\n".join(roles)
            embed = discord.Embed(title=f"{str(user)}",
                                  description=f"Created At: {user.created_at.strftime('%b %d, %Y %I:%M %p')}\n Joined At: {user.joined_at.strftime('%b %d, %Y %I:%M %p')}",
                                  timestamp=datetime.datetime.utcnow(), color=user.top_role.color)
            embed.set_thumbnail(url=user.avatar_url)
            embed.set_footer(
                text=f"Requested by {str(msgAuthor)}", icon_url=msgAuthor.avatar_url)
            embed.add_field(
                name="Info:", value=f"Nickname: {user.nick} \nID: {user.id}")
            embed.add_field(name="Roles:", value=roles)

        elif isinstance(user, discord.User):
            embed = discord.Embed(title=f"{str(user)}",
                                  description=f"Created At: {user.created_at.strftime('%b %d, %Y %I:%M %p')}\n Joined At: User is not in the guild",
                                  timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=user.avatar_url)
            embed.set_footer(
                text=f"Requested by {str(msgAuthor)} NOTE: This user is not in the guild.", icon_url=msgAuthor.avatar_url)

        else:
            embed = discord.Embed(title="An error occurred.")
        await ctx.send(embed=embed)

    @commands.command(help="Returns an invite for bot.")
    async def invite(self, ctx):
        author = ctx.author
        inviteUrl = f"Here's the bot invite, <https://penguin.vaskel.xyz/invite>"
        await ctx.send(inviteUrl)

    @commands.command()
    async def prefixes(self, ctx):
        """Displays bots prefixes for the current server"""
        p = await self.bot.get_prefix(ctx.message)
        l = [i for i in p if i not in (
            f'<@{self.bot.user.id}> ', f'<@!{self.bot.user.id}> ',)]
        await ctx.send(
            embed=discord.Embed(description=f"My prefix for this guild is `{l[0]}`, but you can also mention me!",
                                color=discord.Color.from_rgb(48, 162, 242)))

    @commands.command()
    async def emoji(self, ctx, emoji: discord.PartialEmoji):
        """Displays info about an emoji"""
        embed = discord.Embed(title=f"\{str(emoji)} [{emoji.id}]")
        embed.set_image(url=emoji.url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["guildinfo"])
    async def serverinfo(self, ctx):
        """Displays the server info"""
        guild = ctx.guild
        embed = discord.Embed(
            title=f"Info about {guild.name} ({guild.id})", description=guild.description)
        embed.set_thumbnail(url=str(guild.icon_url))
        embed.add_field(name="Member Count",
                        value=f"Members: {guild.member_count}")
        embed.add_field(name="Owner", value=str(guild.owner), inline=True)
        embed.add_field(name="Region", value=guild.region, inline=True)
        embed.add_field(name="Emojis", value=len(guild.emojis), inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def suggest(self, ctx, *, suggestion):
        """Sends a suggestion to the bot discord server"""
        if len(suggestion) > 200:
            await ctx.send("Suggestion is too long! It must be below 200 chars!")
            return
        channel = self.bot.get_channel(self.bot.config['suggestions-channel'])
        embed = discord.Embed(
            title="New Suggestion", timestamp=datetime.datetime.utcnow(), url=ctx.message.jump_url)
        embed.add_field(name=f"Suggestion #{len(await self.bot.db.fetch('SELECT id FROM suggestions')) + 1}",
                        value=suggestion)
        embed.set_footer(text=f"Suggested By: {str(ctx.author)}")
        await self.bot.db.execute("INSERT INTO suggestions(text, status, date) VALUES($1, $2, $3)", suggestion, "new",
                                  datetime.datetime.utcnow())
        await ctx.send("Suggestion Sent!")
        await channel.send(embed=embed)

    @commands.command()
    async def uptime(self, ctx):
        """Displays the uptime"""
        delta_uptime = datetime.datetime.utcnow() - self.bot.start_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(embed=discord.Embed(description=f"{days}d, {hours}h, {minutes}m, {seconds}s"))

    @commands.group(name="suggestion", aliases=["suggestions"])
    @commands.guild_only()
    async def suggestion(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("No subcommand invoked, please use `help suggestion`!")

    @suggestion.command()
    @commands.guild_only()
    async def view(self, ctx, suggestion: int):
        """Allows you to view a suggestion"""
        colors = {"approved": discord.Color.green(
        ), "rejected": discord.Color.red(), "new": discord.Color.teal()}
        s = await self.bot.db.fetchrow("SELECT * FROM suggestions WHERE ID = $1", suggestion)
        if s is None:
            await ctx.send("Invalid suggestion number")
            return
        embed = discord.Embed(
            title=f"Suggestion #{s['id']}", color=colors[s['status']], timestamp=s['date'])
        embed.add_field(name="Status:", value=s['status'])
        embed.add_field(name="Content:", value=s['text'], inline=False)
        await ctx.send(embed=embed)

    @suggestion.command(name="status")
    @commands.is_owner()
    async def change_status(self, ctx, id: int, status: str):
        """Change the status of a suggestion, use `approved`, `rejected`, or `new`"""
        embColors = {"approved": discord.Color.green(),
                     "rejected": discord.Color.red(), "new": discord.Color.teal()}
        s = await self.bot.db.fetch("SELECT id FROM suggestions")
        if id not in range(1, len(s) + 1):
            await ctx.send("Invalid ID")
            return
        if status not in ["approved", "rejected", "new"]:
            await ctx.send("Invalid status, use approved, rejected, or new.")
        await self.bot.db.execute("UPDATE suggestions SET status = $1 WHERE id = $2", status, id)
        await ctx.send(embed=discord.Embed(description=f"Changed the status of Suggestion `{id}` to `{status}`"))
        channel = self.bot.get_channel(self.bot.config['suggestions-channel'])
        await channel.send(
            embed=discord.Embed(description=f"Suggestion {id} status changed to {status}", color=embColors[status]))

    @suggestion.command(name="delete")
    @commands.is_owner()
    async def remove_suggestion(self, ctx, id: int):
        """Removes a suggestion by setting the text"""
        s = await self.bot.db.fetch("SELECT id FROM suggestions")
        if id not in range(1, len(s) + 1):
            await ctx.send("Invalid ID")
            return
        await self.bot.db.execute("UPDATE SUGGESTIONS SET text = $1, status = $2 WHERE id = $3",
                                  "Removed by the bot owner.", "rejected", id)
        await ctx.send(embed=discord.Embed(description=f"Deleted suggestion `{id}`"))
        channel = self.bot.get_channel(self.bot.config['suggestions-channel'])
        await channel.send(embed=discord.Embed(description=f"Suggestion {id} deleted.", color=discord.Color.red()))

    @commands.command()
    async def privacy(self, ctx):
        """Returns a link to the bots privacy policy."""
        await ctx.embed(title="Privacy Link", url="https://penguin.vaskel.xyz/privacy")

    @commands.command()
    async def stats(self, ctx):
        embed = discord.Embed(description=f"""
        <:members:779771257905479720> Members - {len(self.bot.users)}
        <:dpy:779771889148493835> Discord.py Version - {discord.__version__}
        <:python:779772006710771744> Python Version - {platform.python_version()}
        :notepad_spiral: Commands - {len(self.bot.commands)}""")
        await ctx.send(embed=embed)

    @commands.command()
    async def support(self, ctx):
        await ctx.send("Join the support server! \n<https://penguin.vaskel.xyz/support>")

    @commands.command()
    async def source(self, ctx, *, command: str = None):
        """Returns a link to my source code :)"""
        await ctx.send(("Here's a link to my repo :) make sure to abide by the license \n"
                        "<https://github.com/imvaskel/penguin-bot>"))

    @commands.command()
    async def roleinfo(self, ctx, role: discord.Role = None):
        if not role:
            role = ctx.author.top_role
        permsList = [perm for perm in dict(
            role.permissions) if dict(role.permissions)[perm]]
        embed = discord.Embed(
            title=f"Role Info for `{role.name}`",
            color=role.color
        )
        embed.add_field(
            name="Permissions",
            value="   ".join(
                permsList) if permsList else "No special permissions"
        )
        embed.add_field(
            name="General Information",
            value=f"""
Created At: {role.created_at.strftime('%b %d, %Y %I:%M %p')}
ID: {role.id}
Hoisted: {role.hoist}
Position: {role.position}
Mentionable: {role.mentionable}
Color: {role.color}
Default Role: {role.is_default()}
Mention: {role.mention}""",
            inline=False
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=["pfp"])
    async def avatar(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await ctx.send(embed=discord.Embed(
            title=f"{str(user)}'s profile picture"
        ).set_image(url=str(user.avatar_url)))

    @commands.command()
    async def vote(self, ctx):
        """Returns voting links"""
        embed = discord.Embed(title="__Voting Links__",
                              description="[Top.GG](https://top.gg/bot/753037464599527485) \n[Discord Extreme List](https://discordextremelist.xyz/en-US/bots/penguin)")

        await ctx.send(embed=embed)

    @commands.command()
    async def announcement(self, ctx):
        await ctx.send(embed = discord.Embed(title = "Announcement",
                                             description=self.bot.announcement))

    @commands.command()
    async def dashboard(self, ctx):
        """Returns a link to the dashboard"""
        await ctx.embed(title="Dashboard", url=f"{self.bog.config['website']}config/")

    @commands.command()
    async def website(self, ctx):
        """Returns the website link"""
        await ctx.embed(title="Website", url=f"{self.bot.config['website']}")


def setup(bot):
    bot.add_cog(MembersCog(bot))
