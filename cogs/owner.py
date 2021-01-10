import discord
from discord.ext import commands, menus
import os
import subprocess as sp
from jishaku import codeblocks
from .utils.paginator import SimplePages


class SqlEntry:
    __slots__ = ('data')

    def __init__(self, entry):
        self.data = str(entry)

    def __str__(self):
        return f'{self.data}'


class SqlPages(SimplePages):
    def __init__(self, entries, *, per_page=12):
        converted = [SqlEntry(entry) for entry in entries]
        super().__init__(converted, per_page=per_page)


class OwnerCog(commands.Cog, name="Owner", command_attrs=dict(hidden=True)):
    """Owner Commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='load', hidden=True)
    async def load_cog(self, ctx, *, cog: str):
        # Command which Loads a Module.
        # Remember to use dot path. e.g: cogs.owner

        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def unload_cog(self, ctx, *, cog: str):
        # Command which Unloads a Module.
        # Remember to use dot path. e.g: cogs.owner

        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def reload_cog(self, ctx, *, cog: str):
        # Command which Reloads a Module.
        # Remember to use dot path. e.g: owner

        try:
            self.bot.reload_extension(cog)
            await ctx.send(f"Reloaded cog {cog}")
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(hidden=True, aliases=["reloadall", "ra"])
    @commands.is_owner()
    async def reload_all(self, ctx):
        succesful = []
        unseccesful = []
        extensions = list(self.bot.extensions.keys())

        for cog in extensions:
            try:
                self.bot.reload_extension(cog)
                succesful.append(cog)
            except:
                unseccesful.append(cog)

        embed = discord.Embed(title="Reloaded all extensions")

        embed.add_field(name="Successful",
                        value="\t".join(succesful) or "None")
        embed.add_field(name="Unsuccessful",
                        value="\t".join(unseccesful) or "None")

        await ctx.send(embed=embed)

    @commands.command(name='cogs', hidden=True)
    @commands.is_owner()
    async def active_cogs(self, ctx):
        s = str.join('\n', self.bot.cogs.keys())
        await ctx.send(embed=discord.Embed(title="Active Cogs:", description=f"```{s}```"))

    @commands.command(name="restart", hidden=True)
    @commands.is_owner()
    async def nopnop(self, ctx):
        """Restarts the bot
        Uses: `p,restart`"""
        owner = self.bot.get_user(self.bot.owner_id)
        embedvar = discord.Embed(
            title="*Restarting...*", description="Be right back!")
        embedvar.set_footer(text=f"Bot made by {owner}")
        await ctx.send(embed=embedvar)
        await self.bot.logout()

    @commands.command(aliases=['update', 'maintenence', 'logout', 'die', 'kill'], hidden=True,)
    @commands.is_owner()
    async def shutdown(self, ctx):
        """Shuts the bot down
        Uses: `p,shutdown`"""
        embedvar = discord.Embed(
            title="*Killing Bot* \U0001f52a", description="Goodbye!", color=0xff0000)
        await ctx.send(embed=embedvar)
        print("Bot Shut Down")
        output = sp.getoutput("systemctl --user stop penguin")
        await ctx.send(output)

    @commands.is_owner()
    @commands.group(hidden=True, name="activity")
    async def _activity(self, ctx):
        """A command that changes status playing and more."""
        if ctx.invoked_subcommand is None:
            await ctx.send(f'Incorrect block subcommand passed.')

    @commands.is_owner()
    @_activity.command()
    async def playing(self, ctx, *, activity: str):
        """Sets playing status in silent."""
        await self.bot.change_presence(activity=discord.Game(name=activity))

    @commands.is_owner()
    @_activity.command()
    async def watching(self, ctx, *, activity: str):
        """Sets watching status in silent."""
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activity))

    @commands.is_owner()
    @_activity.command()
    async def listening(self, ctx, *, activity: str):
        """Sets listening status in silent."""
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activity))

    @commands.command(aliases=['pull'], hidden=True)
    @commands.is_owner()
    async def sync(self, ctx):
        """Get the most recent changes from the GitHub repository
        Uses: p,sync"""
        embedvar = discord.Embed(title="Syncing...", description="Syncing with the GitHub repository, this should take up to 15 seconds",
                                 color=0xff0000, timestamp=ctx.message.created_at)
        msg = await ctx.send(embed=embedvar)
        async with ctx.channel.typing():
            c = self.bot.get_guild(
                765977212498870305).get_channel(766011513156665385)
            output = sp.getoutput('git pull origin master')
            await c.send(f""" ```sh
            {output} ```""")
            msg1 = await ctx.send("Success!")
            await msg1.delete()
        embedvar = discord.Embed(title="Synced", description="Sync with the GitHub repository has completed, check the logs to make sure it worked",
                                 color=0x00ff00, timestamp=ctx.message.created_at)
        await msg.edit(embed=embedvar)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload_db(self, ctx):
        self.bot.prefixes = dict(await self.bot.db.fetch("SELECT id, prefix FROM guild_config"))
        await ctx.send(embed=discord.Embed(title="\u200b", description=f"Reloaded db"))

    @commands.is_owner()
    @commands.group(hidden=True, name="force")
    async def force(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(f'Incorrect block subcommand passed.')

    @force.command()
    @commands.guild_only()
    @commands.is_owner()
    async def prefix(self, ctx, newPrefix: str):

        if not ctx.guild.id in self.bot.prefixes:
            await self.bot.db.execute(f'INSERT INTO guild_config(id, prefix) VALUES($1, $2)', ctx.guild.id, newPrefix)
        elif ctx.guild.id in self.bot.prefixes:
            await self.bot.db.execute("UPDATE guild_config SET prefix = $2 WHERE id = $1", ctx.guild.id, newPrefix)
        self.bot.prefixes = dict(await self.bot.db.fetch("SELECT id, prefix FROM guild_config"))
        await ctx.send(embed=discord.Embed(description=f"Set {str(ctx.guild)}'s prefix to  {newPrefix}."))

    @force.command()
    @commands.is_owner()
    async def leave(self, ctx):
        await ctx.send(f"Leaving {ctx.guild.name}, goodbye!")
        await ctx.guild.leave()

    @commands.is_owner()
    @commands.command(hidden=True)
    async def eval(self, ctx, *, code: str = None):
        if code is None:
            return await ctx.send('No arg given')
        await ctx.invoke(self.bot.get_command('jsk py'), argument=codeblocks.codeblock_converter(code))

    @commands.is_owner()
    @commands.command(hidden=True)
    async def debug(self, ctx, *, command: str = None):
        if str is None:
            return await ctx.send('No arg given')
        await ctx.invoke(self.bot.get_command('jsk dbg'), command_string=command)

    @commands.is_owner()
    @commands.command(hidden=True)
    async def shell(self, ctx, *, arg: str = None):
        if str is None:
            return await ctx.send('No arg given')
        await ctx.invoke(self.bot.get_command('jsk shell'), argument=codeblocks.codeblock_converter(arg))

    @commands.is_owner()
    @commands.command(hidden=True)
    async def reply(self, ctx, messageId, *, reply=None):
        if not reply:
            return await ctx.reply("You didn't provide a reply!")
        e = await ctx.fetch_message(messageId)
        await e.reply(reply)

    @commands.is_owner()
    @commands.command(hidden=True)
    async def sql(self, ctx, *, query):
        """Makes an sql SELECT query"""
        query = codeblocks.codeblock_converter(query)[1]
        e = await self.bot.db.fetch(query)
        try:
            p = SqlPages(entries=e, per_page=10)
            await p.start(ctx)
        except menus.MenuError as f:
            await ctx.send(f)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def refresh_db(self, ctx):
        """Reboots the db connection"""
        m = await ctx.send("Refreshing......")
        try:
            await self.bot.refresh_connection()
            await m.edit(content="Refreshed the DB connection")
        except:
            await m.edit("An unknown error occured......")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def refresh_cache(self, ctx):
        """Refreshes the cache"""
        m = await ctx.send("Refreshing......")
        try:
            await self.bot.refresh_cache()
            await m.edit(content="Refreshed the cache")
        except:
            await m.edit("An unknown error occured......")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def journalctl(self, ctx):
        await ctx.invoke(self.bot.get_command('jsk sh'), argument=codeblocks.codeblock_converter("journalctl -u penguin"))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def blacklist(self, ctx, user: discord.User):
        try:
            await self.bot.db.execute("INSERT INTO blacklist(id) VALUES($1)", user.id)
            await ctx.reply("User blacklisted.")
            await self.bot.refresh_blacklist()
        except Exception as e:
            await ctx.reply(f"An error occured \n{e}")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unblacklist(self, ctx, user: discord.User):
        try:
            await self.bot.db.execute("DELETE FROM blacklist where id = $1", user.id)
            await ctx.reply("User unblacklisted.")
            await self.bot.refresh_blacklist()
        except Exception as e:
            await ctx.reply(f"An error occured \n{e}")

    @commands.command()
    @commands.is_owner()
    async def set_announcement(self, ctx, *, announcement):
        try:
            with open('announcement.txt', 'w+') as file:
                file.truncate(0)
                file.write(announcement)
        except Exception as e:
            return await ctx.reply("An error occurred ``` \n" + str(e) + "```")

        self.bot.announcement = announcement
        await ctx.reply("Successfully set the announcement")



def setup(bot):
    bot.add_cog(OwnerCog(bot))
