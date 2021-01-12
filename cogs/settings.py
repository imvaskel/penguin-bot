import discord
from discord.ext import commands
from listeners.errors import ErrorEmbed


class SettingsCog(commands.Cog, name="Settings"):
    """Cog that deals with settings of the bot, you must have the `manage guild` permission to use this."""

    def __init__(self, bot):
        self.bot = bot
        self.off_on = ["<:set_no_on:776868727257825330><:set_yes_off:776868727257825290>",  # off
                       "<:set_no_off:776868727253237780><:set_yes_on:776868727089659905>"]  # on

    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.manage_guild

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            return await ctx.reply(embed=ErrorEmbed(description="You don't have the `mange guilds` permission."))

    @commands.command()
    @commands.guild_only()
    async def set_prefix(self, ctx, newPrefix: str):

        if ctx.guild.id not in self.bot.prefixes:
            await self.bot.db.execute('INSERT INTO guild_config(id, prefix) VALUES($1, $2)', ctx.guild.id, newPrefix)
        elif ctx.guild.id in self.bot.prefixes:
            await self.bot.db.execute("UPDATE guild_config SET prefix = $2 WHERE id = $1", ctx.guild.id, newPrefix)

        self.bot.prefixes = dict(await self.bot.db.fetch("SELECT id, prefix FROM guild_config"))
        await ctx.send(embed=discord.Embed(description=f"Set {ctx.guild}'s prefix to {newPrefix}."))

    @commands.guild_only()
    @commands.group(name="reactionroles", aliases=['reaction_roles', 'reactionrole', 'reaction_role'])
    async def reactionroles(self, ctx):
        """A command that deals with reaction roles."""
        if ctx.invoked_subcommand is None:
            await ctx.send(f'Incorrect block subcommand passed.')

    @reactionroles.command(help="Adds a reaction role on the given message, to delete it run `reactionrole remove <id>`", name='add')
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def reaction_roles_add(self, ctx, message: discord.Message, role: discord.Role):
        if role > ctx.guild.me.top_role or role == ctx.guild.me.top_role:
            return await ctx.send("That role is either above me or is my top role!")
        await message.add_reaction("\U00002705")
        await self.bot.db.execute("INSERT INTO reaction_roles(msg_id, role_id, guild_id) VALUES ($1, $2, $3)", message.id, role.id, ctx.guild.id)
        self.bot.reactionRoleDict = dict(await self.bot.db.fetch("SELECT msg_id, role_id FROM reaction_roles"))
        await ctx.send(embed=discord.Embed(description=f"Added a reaction role to {message.id} that gives role {role.name}"))

    @reactionroles.command(help="Removes a reaction role from the given message id", name='remove')
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def reaction_roles_remove(self, ctx, messageId: int):
        await self.bot.db.execute("DELETE FROM reaction_roles WHERE msg_id = $1", messageId)
        self.bot.reactionRoleDict = dict(await self.bot.db.fetch("SELECT msg_id, role_id FROM reaction_roles"))
        await ctx.send(embed=discord.Embed(description=f"Removed the reaction role from the message id {messageId}"))

    @reactionroles.command(help="Lists the current reaction roles in the guild with their message id and the role id", name='list')
    @commands.guild_only()
    async def reaction_roles_list(self, ctx):
        l = ""
        for entry in await self.bot.db.fetch("SELECT msg_id, role_id FROM reaction_roles WHERE guild_id = $1", ctx.guild.id):
            l += f"Message ID: {entry[0]} Role ID: {entry[1]}\n"
        await ctx.send(embed=discord.Embed(description=l, color=discord.Color.from_rgb(48, 162, 242)))

    @commands.guild_only()
    @commands.group(name="log")
    async def log_group(self, ctx):
        """A command that deals with the bots logging."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @log_group.command(name='set')
    @commands.guild_only()
    async def set_log(self, ctx, channel: discord.TextChannel):
        if not channel.permissions_for(ctx.me).send_messages:
            raise commands.BadArgument(
                "I cannot send messages in that channel. Please give me permissions to send messages in that channel.")

        await self.bot.db.execute("""UPDATE guild_config SET log_id = $1 WHERE id = $2""", channel.id, ctx.guild.id)

        await ctx.reply(embed=discord.Embed(description=f"Set {channel.mention} to this guild's log channel."))

        await self.bot.refresh_cache_for(ctx.guild.id)

    @log_group.command(name='remove')
    @commands.guild_only()
    async def remove_log(self, ctx):
        if not self.bot.cache[ctx.guild.id]['logId']:
            raise commands.BadArgument(
                "This guild does not have a log channel set.")

        await self.bot.db.execute("UPDATE guild_config SET log_id = NULL WHERE id = $1", ctx.guild.id)

        await ctx.reply("Successfully removed the log channel for this guild.")

        await self.bot.refresh_cache_for(ctx.guild.id)

    @log_group.command(name='view')
    @commands.guild_only()
    async def view_log(self, ctx):
        if logId := self.bot.cache[ctx.guild.id]['logId']:
            channel = ctx.guild.get_channel(logId)
            await ctx.reply(f"The log channel for this server is {channel.id}")
        else:
            raise commands.BadArgument("This guild has no log channel set.")

    @commands.guild_only()
    @commands.group(name="welcomer")
    async def welcomer_group(self, ctx):
        """Command group that deals with welcoming"""
        if ctx.invoked_subcommand is None:
            await ctx.send("No subcommand passed, use `help welcomer` for help.")

    @welcomer_group.command(name="set", aliases=["set_channel"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def set_welcomer_channel(self, ctx, channel: discord.TextChannel):
        """Sets the welcoming channel"""
        if not channel.permissions_for(ctx.guild.me).send_messages:
            return await ctx.send("I can't send messages in that channel!")
        if ctx.guild.id not in self.bot.welcome_dict:
            await self.bot.db.execute("UPDATE welcome SET welcomeid = $2 WHERE id = $1", ctx.guild.id, channel.id)
        elif ctx.guild.id in self.bot.welcome_dict:
            await self.bot.db.execute("UPDATE guild_config SET welcomeid = $1 WHERE id = $2", channel.id, ctx.guild.id)
        await ctx.send(embed=discord.Embed(description=f"Set {channel.mention} as the welcoming channel."))

    @welcomer_group.command(name="set_message")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def welcome_message(self, ctx, *, message: str):
        """Sets the welcome message USE `help welcomer set_message` this includes formatting!
            ```
            {user.mention} replaces with @user
            {user.name} replaces with user#xxxx
            {user.id} replaces with the users id
            {guild.name} replaces with the guilds name
            {guild.id} replaces with the guilds id
            ```
        """
        await self.bot.db.execute("UPDATE guild_config SET welcomeMessage = $1 WHERE id = $2", message, ctx.guild.id)
        await ctx.send(f"Changed the welcome message to ```{message}```")
        await self.bot.refresh_cache_for(ctx.guild.id)

    @welcomer_group.command(name="delete", aliases=["remove_channel"])
    @commands.guild_only()
    async def remove_welcomer_channel(self, ctx):
        """Removes the welcomer channel, which also disables the bot welcoming."""
        await self.bot.db.execute("UPDATE guild_config SET welcomeId = NULL")
        await ctx.send(embed=discord.Embed(description=f"Removed the welcome channel and disabled welcomer."))
        await self.bot.refresh_cache_for(ctx.guild.id)

    @welcomer_group.command(name="disable")
    @commands.guild_only()
    async def welcomer_disable(self, ctx):
        if not self.bot.cache[ctx.guild.id]["welcomeEnabled"]:
            return await ctx.send("Welcomer is already disabled!")
        await self.bot.db.execute("UPDATE guild_config SET welcomeEnabled = FALSE")
        await ctx.send("Disabled the welcomer, use `welcomer enable` to reenable")
        await self.bot.refresh_cache_for(ctx.guild.id)

    @welcomer_group.command(name="enable")
    @commands.guild_only()
    async def welcomer_enable(self, ctx):
        if self.bot.cache[ctx.guild.id]["welcomeEnabled"]:
            return await ctx.send("Welcomer is already enabled!")
        await self.bot.db.execute("UPDATE guild_config SET welcomeEnabled = TRUE")
        await ctx.send("Enabled the welcomer, use `welcomer disable` to disable")
        await self.bot.refresh_cache_for(ctx.guild.id)

    @commands.group(name="autorole", aliases=["autoroles"])
    @commands.guild_only()
    async def autorole_group(self, ctx):
        """Autorole commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @autorole_group.command(name="add")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def autorole_add(self, ctx, role: discord.Role):
        """Adds auto role"""
        if role > ctx.guild.me.top_role or role == ctx.guild.me.top_role:
            return await ctx.send("That role is either above me or is my top role!")
        await self.bot.db.execute("UPDATE guild_config SET autorole = $1 WHERE id = $2", role.id, ctx.guild.id)
        await ctx.send(embed=discord.Embed(description=f"Added autorole for role {role.mention}."))
        await self.bot.refresh_cache_for(ctx.guild.id)

    @autorole_group.command(name="remove")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def autorole_remove(self, ctx):
        """Removes guilds autorole"""
        await self.bot.db.execute("UPDATE guild_config SET autorole = null WHERE id = $1", ctx.guild.id)
        await ctx.send(embed=discord.Embed(description=f"Removed autorole"))
        await self.bot.refresh_cache_for(ctx.guild.id)

    @autorole_group.command(name="role")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def autorole_list(self, ctx):
        """Lists autoroles"""
        s = await self.bot.db.fetchrow("SELECT autorole FROM guild_config WHERE id = $1", ctx.guild.id)
        role = ctx.guild.get_role(s["autorole"])
        await ctx.send(embed=discord.Embed(description=f"{str(ctx.guild)}'s autorole is {role}"))

    @commands.command(aliases=['settings'])
    @commands.guild_only()
    async def configs(self, ctx):
        """Returns the state of the guilds configs"""
        template = "ட {}\n"
        guildCache = self.bot.cache[ctx.guild.id]
        embed = discord.Embed(title="Configs",
                              description=(
                                  f"Prefix : `{guildCache['prefix']}`\n"
                                  f"{self.off_on[bool(guildCache['autorole'])]} Autorole\n"
                                  f"{self.off_on[bool(guildCache['welcomeId'])]} Welcome\n"
                                  f"{self.off_on[bool(guildCache['logId'])]} Logging"
                              ))
        await ctx.send(embed=embed)
        await ctx.refresh_cache()


def setup(bot):
    bot.add_cog(SettingsCog(bot))
