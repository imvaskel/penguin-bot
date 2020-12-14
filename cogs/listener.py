import discord, re, asyncio, datetime
from discord import member
from discord import guild
from discord.ext import commands

template_vars = {
    '{user.mention}': lambda m: m.mention,
    '{user.name}': lambda m: str(m),
    '{user.id}': lambda m: str(m.id),
    '{guild.name}': lambda m: m.guild.name,
    '{guild.id}': lambda m: str(m.guild.id),
}
template_re = re.compile('({})'.format('|'.join(re.escape(var) for var in template_vars)))
def format_message(member, template):
    def replacer(match):
        return template_vars[match.group(1)](member)
    return template_re.sub(replacer, template)

class ListenerCog(commands.Cog, name = "Listener"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content in ("<@!753037464599527485>", "<@753037464599527485>"):
            p = await self.bot.get_prefix(message)
            l = [i for i in p if i not in (f'<@{self.bot.user.id}> ', f'<@!{self.bot.user.id}> ',)]
            await message.reply(embed = discord.Embed(description = f"My prefix for this guild is `{l[0]}`, but you can also mention me!", color = discord.Color.from_rgb(48,162,242)))

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        try:
            await self.bot.db.execute(f"INSERT INTO guild_config(id) VALUES ($1)", guild.id)
        except:
            pass
        p = await self.bot.db.fetchrow("SELECT id, prefix FROM guild_config WHERE id = $1", guild.id)
        self.bot.prefixes[guild.id] = p['prefix']
        record = await self.bot.db.fetchrow("SELECT * FROM guild_config WHERE id = $1", guild.id)
        d = {
  record["id"]: {"prefix": record["prefix"], "log_id": record["log_id"], "log_enabled": record["log_enabled"], "autorole": record["autorole"], "welcomeMessage": record["welcomemessage"], "welcomeEnabled": record["welcomeenabled"], "welcomeId": record["welcomeid"]}
}
        self.bot.cache.update(d)
        print(f"I have joined {guild.name} [{guild.id}]")
        c = self.bot.get_channel(781615213421658142)
        # Guild information sent to this channel
        embed = discord.Embed(
            title = "Guild Joined!",
            description = f"""```yaml
Guild Name - {str(guild)}
Guild ID - {guild.id}
Guild Owner - {str(guild.owner)} [{guild.id}]
Guild Created - {guild.created_at.strftime('%b %d, %Y %I:%M %p')}
Guild Members - {len(guild.members)}
```""",
            timestamp = datetime.datetime.utcnow()
        )
        await c.send(embed = embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        try:
            await self.bot.db.execute("DELETE FROM guild_config WHERE id = $1", guild.id)
        except:
            pass

        print(f"I have left {guild.name} [{guild.id}]")
        c = self.bot.get_channel(781615213421658142)
        # Guild information sent to this channel
        embed = discord.Embed(
            title = "Guild Left!",
            description = f"""```yaml
Guild Name - {str(guild)}
Guild ID - {guild.id}
Guild Owner - {str(guild.owner)} [{guild.owner.id}]
Guild Created - {guild.created_at.strftime('%b %d, %Y %I:%M %p')}
Guild Members - {len(guild.members)}
```""",
            timestamp = datetime.datetime.utcnow()
        )
        await c.send(embed = embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if int(payload.message_id) in self.bot.reactionRoleDict and str(payload.emoji) == "\U00002705":
            guild = self.bot.get_guild(int(payload.guild_id))
            member = guild.get_member(int(payload.user_id))
            role = guild.get_role(self.bot.reactionRoleDict[int(payload.message_id)])
            await member.add_roles(role, reason = "Reaction Role")
        else:
            return

    @commands.Cog.listener()
    async def on_member_join(self, member):
        e = self.bot.cache[member.guild.id]
        try:
            if e["welcomeEnabled"]:
                try: s = await self.bot.fetch_channel(e["welcomeId"])
                except: return
                if not e["welcomeMessage"] or e["welcomeMessage"] == "_default":
                    try:await s.send(f"Welcome **{str(member)}** to {str(member.guild)}!")
                    except discord.Forbidden: return
                else:
                    message = format_message(member, e["welcomeMessage"])
                    try:await s.send(message)
                    except discord.Forbidden: return
        except KeyError: return

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.content != after.content:
            ctx = await self.bot.get_context(after)
            await self.bot.invoke(ctx)

def setup(bot):
    bot.add_cog(ListenerCog(bot))
