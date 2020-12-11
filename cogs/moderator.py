import discord
from discord.ext import commands
from discord.ext.commands.core import command


class ModeratorCog(commands.Cog, name = "Moderator"):
    """Commands for moderators"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members = True)
    @commands.bot_has_permissions(kick_members = True)
    async def kick(self, ctx, member: discord.Member, *, reason = None):
        """Kicks a user, you can use `Username` `Username#discriminator` or `userId`"""
        if member.id == ctx.author.id: return await ctx.send("You can't do that to yourself!") 
        if member.top_role > ctx.me.top_role or member.top_role == ctx.me.top_role: return await ctx.send("That member's top role is higher or equal to mine!")
        try:await member.send(f"You were kicked from {ctx.guild.name} for {reason}")
        except discord.HTTPException: pass
        await member.kick(reason=reason)
        await ctx.send(f"Kicked {member.name} for {reason}")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
    @commands.bot_has_permissions(ban_members = True)
    async def ban(self, ctx, member: discord.Member, *, reason = None):
        """Bans a user, you can use `Username` `Username#discriminator` or `userId`"""
        if member.id == ctx.author.id: return await ctx.send("You can't do that to yourself!") 
        if member.top_role > ctx.me.top_role or member.top_role == ctx.me.top_role: return await ctx.send("That member's top role is higher or equal to mine!")
        guild = ctx.guild
        try: await member.send(f"You were banned from {guild.name} for {reason}")
        except discord.HTTPException: pass
        await guild.ban(member, reason = reason)
        await ctx.send(f"{member.name} was banned for {reason}.")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
    @commands.bot_has_permissions(ban_members = True)
    async def unban(self, ctx, user: int, *, reason = None):
        """Unbans a user with a given ID"""
        if user == ctx.author.id: return await ctx.send("You can't do that to yourself!") 
        member = discord.Object(id = user)
        try: 
            await ctx.guild.unban(member)
            await ctx.send(embed  = discord.Embed(description = f"Unbanned {member.id} for {reason}."))
        except discord.NotFound: return await ctx.send(embed = discord.Embed(description = "That user doesn't seem to be banned."))

    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages = True)
    @commands.command(help ="Clears X messages up to 500, also can do only Y member's messages")
    async def clear(self, ctx, num: int, target: discord.Member=None):
        if num > 500 or num < 0:
            return await ctx.send("Invalid amount. Maximum is 500.")
        def msgcheck(amsg):
            if target:
                return amsg.author.id == target.id
            return True
        deleted = await ctx.channel.purge(limit=num, check=msgcheck)
        await ctx.send(f':thumbsup: Deleted **{len(deleted)}/{num}** possible messages for you.', delete_after=10)

    @commands.has_permissions(manage_roles = True)
    @commands.bot_has_permissions(manage_roles = True)
    @commands.guild_only()
    @commands.command()
    async def block(self, ctx, user: discord.Member = None):
        """Blocks a user from sending messages in the channel"""
        if user == ctx.author.id: return await ctx.send("You can't do that to yourself!") 
        if user.top_role > ctx.me.top_role or user.top_role == ctx.me.top_role: return await ctx.send("That member's top role is higher or equal to mine!")
        if user.top_role > ctx.author.top_role or user.top_role == ctx.author.top_role: return await ctx.send("That member's top role is higher or equal to yours!")
        channel = ctx.channel
        if user == None:
            await ctx.send("User not specified, try again.")
        
        await channel.set_permissions(user, send_messages=False)
        await ctx.send(f"{user} was blocked from the channel.")
    
    @commands.has_permissions(manage_roles = True)
    @commands.bot_has_permissions(manage_roles = True)
    @commands.guild_only()
    @commands.command()
    async def unblock(self, ctx, user: discord.Member = None):
        """Unblocks the given user from the channel:"""
        if user.top_role > ctx.me.top_role or user.top_role == ctx.me.top_role: return await ctx.send("That member's top role is higher or equal to mine!")
        if user.top_role > ctx.author.top_role or user.top_role == ctx.author.top_role: return await ctx.send("That member's top role is higher or equal to yours!")
        channel = ctx.channel
        if user == None:
            await ctx.send("User not specified, try again.")
        
        await channel.set_permissions(user, send_messages=True)
        await ctx.send(f"{user} was unblocked from the channel.")
    
    @commands.has_permissions(manage_channels = True)
    @commands.bot_has_permissions(manage_channels = True)
    @commands.guild_only()
    @commands.command(help = "Adds a slowmode to a channel in seconds, use no arg or 0 to remove slowmode.")
    async def slowmode(self, ctx, seconds: int = None):
        channel = ctx.channel 
    
        if seconds == None:
            await channel.edit(slowmode_delay=0)
        
        await channel.edit(slowmode_delay=seconds)

    @commands.has_permissions(manage_guild = True)
    @commands.command(description = "Leaves guild, only useable by users with the administrator role.")
    async def leave(self, ctx):
        await ctx.send(f"Leaving server {ctx.guild.name}, goodbye.")
        print(f"Left server {ctx.guild.name}")
        await ctx.guild.leave()
    
    @commands.command(description = "This bans a user, but saves their messages.")
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
    @commands.bot_has_permissions(ban_members = True)
    async def saveban(self, ctx, member: discord.Member, *, reason = None):
        if member.id == ctx.author.id: return await ctx.send("You can't do that to yourself!") 
        if member.top_role > ctx.me.top_role or member.top_role == ctx.me.top_role: return await ctx.send("That member's top role is higher or equal to mine!")
        guild = ctx.guild
        try: await member.send(f"You were banned from {guild.name} for {reason}")
        except discord.HTTPException: pass
        await guild.ban(member, delete_message_days = 0, reason = reason)
        await ctx.send(f"{member.name} was banned for {reason}.")
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    async def set_prefix(self, ctx, newPrefix: str):
        
        if not ctx.guild.id in self.bot.prefixes:
            await self.bot.db.execute(f'INSERT INTO guild_config(id, prefix) VALUES($1, $2)', ctx.guild.id, newPrefix)
        elif ctx.guild.id in self.bot.prefixes:
            await self.bot.db.execute("UPDATE guild_config SET prefix = $2 WHERE id = $1", ctx.guild.id, newPrefix)

        self.bot.prefixes = dict(await self.bot.db.fetch("SELECT id, prefix FROM guild_config"))
        await ctx.send(embed = discord.Embed(description = f"Set {str(ctx.guild)}'s prefix to  {newPrefix}."))
    
    @commands.guild_only()
    @commands.group(name="reactionroles", aliases = ['reaction_roles', 'reactionrole', 'reaction_role'])
    async def reactionroles(self, ctx):
        """A command that deals with reaction roles."""
        if ctx.invoked_subcommand is None:
            await ctx.send(f'Incorrect block subcommand passed.')

    @reactionroles.command(help = "Adds a reaction role on the given message, to delete it run `reactionrole remove <id>`")
    @commands.guild_only()
    @commands.has_permissions(manage_roles = True)
    @commands.bot_has_permissions(manage_roles = True)
    async def add(self, ctx, message: discord.Message, role: discord.Role):
        if role > ctx.guild.me.top_role or role == ctx.guild.me.top_role: return await ctx.send("That role is either above me or is my top role!")
        await message.add_reaction("\U00002705")
        await self.bot.db.execute("INSERT INTO reaction_roles(msg_id, role_id, guild_id) VALUES ($1, $2, $3)", message.id, role.id, ctx.guild.id)
        self.bot.reactionRoleDict = dict(await self.bot.db.fetch("SELECT msg_id, role_id FROM reaction_roles"))
        await ctx.send(embed = discord.Embed(description = f"Added a reaction role to {message.id} that gives role {role.name}"))
    
    @reactionroles.command(help = "Removes a reaction role from the given message id")
    @commands.guild_only()
    @commands.has_permissions(manage_roles = True)
    async def remove(self, ctx, messageId: int):
        await self.bot.db.execute("DELETE FROM reaction_roles WHERE msg_id = $1", messageId)
        self.bot.reactionRoleDict = dict(await self.bot.db.fetch("SELECT msg_id, role_id FROM reaction_roles"))
        await ctx.send(embed = discord.Embed(description = f"Removed the reaction role from the message id {messageId}"))

    @reactionroles.command(help = "Lists the current reaction roles in the guild with their message id and the role id")
    @commands.guild_only()
    async def list(self, ctx):
        l = ""
        for entry in await self.bot.db.fetch("SELECT msg_id, role_id FROM reaction_roles WHERE guild_id = $1", ctx.guild.id):
            l += f"Message ID: {entry[0]} Role ID: {entry[1]}\n"
        await ctx.send(embed = discord.Embed(description = l, color = discord.Color.from_rgb(48,162,242)))
    
    @commands.guild_only()
    @commands.group(hidden=True, name="log")
    async def log_group(self, ctx):
        """A command that deals with the bots logging."""
        if ctx.invoked_subcommand is None:
            await ctx.send(f'No subcommand passed.')
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    async def set_log(self, ctx, id: discord.TextChannel):
        """Currently does nothing, please ignore"""
        return
    
    @commands.guild_only()
    @commands.group(name = "welcomer")
    async def welcomer_group(self, ctx):
        """Command group that deals with welcoming"""
        if ctx.invoked_subcommand is None:
            await ctx.send("No subcommand passed, use `help welcomer` for help.")
    
    @welcomer_group.command(name = "set", aliases = ["set_channel"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    async def set_welcomer_channel(self, ctx, channel: discord.TextChannel):
        """Sets the welcoming channel"""
        if not channel.permissions_for(ctx.guild.me).send_messages: return await ctx.send("I can't send messages in that channel!")
        if ctx.guild.id not in self.bot.welcome_dict:
            await self.bot.db.execute("UPDATE welcome SET welcomeid = $2 WHERE id = $1", ctx.guild.id, channel.id)
        elif ctx.guild.id in self.bot.welcome_dict:
            await self.bot.db.execute("UPDATE guild_config SET welcomeid = $1 WHERE id = $2", channel.id, ctx.guild.id)
        await ctx.send(embed= discord.Embed(description = f"Set {channel.mention} as the welcoming channel."))
        
    
    @welcomer_group.command(name = "set_message")
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
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
        self.bot.cache[ctx.guild.id]["welcomeMessage"] = message
    
    @welcomer_group.command(name = "delete", aliases = ["remove_channel"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    async def remove_welcomer_channel(self, ctx):
        """Removes the welcomer channel, which also disables the bot welcoming."""
        await self.bot.db.execute("UPDATE guild_config SET welcomeId = NULL")
        await ctx.send(embed = discord.Embed(description = f"Removed the welcome channel and disabled welcomer."))
        self.bot.cache[ctx.guild.id]["welcomeEnabled"] = False
        self.bot.cache[ctx.guild.id]["welcomeId"] = None
    
    @welcomer_group.command(name = "disable")
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    async def welcomer_disable(self, ctx):
        if not self.bot.cache[ctx.guild.id]["welcomeEnabled"]: return await ctx.send("Welcomer is already disabled!")
        await self.bot.db.execute("UPDATE guild_config SET welcomeEnabled = FALSE")
        await ctx.send("Disabled the welcomer, use `welcomer enable` to reenable")
        self.bot.cache[ctx.guild.id]["welcomeEnabled"] = False

    @welcomer_group.command(name = "enable")
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    async def welcomer_enable(self, ctx):
        if self.bot.cache[ctx.guild.id]["welcomeEnabled"]: return await ctx.send("Welcomer is already enabled!")
        await self.bot.db.execute("UPDATE guild_config SET welcomeEnabled = TRUE")
        await ctx.send("Enabled the welcomer, use `welcomer disable` to disable")
        self.bot.cache[ctx.guild.id]["welcomeEnabled"] = True

    @commands.group(name = "autorole", aliases = ["autoroles"])
    @commands.guild_only()
    async def autorole_group(self, ctx):
        """Autorole commands"""
        if ctx.invoked_subcommand is None: await ctx.send("No subcommand passed, use `help autorole` for help.")
    
    @autorole_group.command(name = "add")
    @commands.guild_only()
    @commands.has_permissions(manage_roles= True)
    @commands.bot_has_permissions(manage_roles = True)
    async def autorole_add(self, ctx, role: discord.Role):
        """Adds auto role"""
        if role > ctx.guild.me.top_role or role == ctx.guild.me.top_role: return await ctx.send("That role is either above me or is my top role!")
        await self.bot.db.execute("UPDATE guild_config SET autorole = $1 WHERE id = $2", role.id, ctx.guild.id)
        await ctx.send(embed = discord.Embed(description = f"Added autorole for role {role.mention}."))
    
    @autorole_group.command(name = "remove")
    @commands.guild_only()
    @commands.has_permissions(manage_roles= True)
    async def autorole_remove(self, ctx):
        """Removes guilds autorole"""
        await self.bot.db.execute("UPDATE guild_config SET autorole = null WHERE id = $1", ctx.guild.id)
        await ctx.send(embed = discord.Embed(description = f"Removed autorole"))
    
    @autorole_group.command(name = "role")
    @commands.guild_only()
    @commands.has_permissions(manage_roles= True)
    async def autorole_list(self, ctx):
        """Lists autoroles"""
        s = await self.bot.db.fetchrow("SELECT autorole FROM guild_config WHERE id = $1", ctx.guild.id)
        role = ctx.guild.get_role(s["autorole"])
        await ctx.send(embed= discord.Embed(description = f"{str(ctx.guild)}'s autorole is {role}"))

def setup(bot):
    bot.add_cog(ModeratorCog(bot))
