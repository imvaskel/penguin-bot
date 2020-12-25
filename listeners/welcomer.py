import discord
from discord.ext import commands
import re

template_vars = {
    '{user.mention}': lambda m: m.mention,
    '{user.name}': lambda m: str(m),
    '{user.id}': lambda m: str(m.id),
    '{guild.name}': lambda m: m.guild.name,
    '{guild.id}': lambda m: str(m.guild.id),
}
template_re = re.compile('({})'.format(
    '|'.join(re.escape(var) for var in template_vars)))

def format_message(member, template):
    def replacer(match):
        return template_vars[match.group(1)](member)
    return template_re.sub(replacer, template)

class WelcomerListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        e = self.bot.cache[member.guild.id]
        try:
            if e["welcomeEnabled"]:
                try:
                    s = await self.bot.fetch_channel(e["welcomeId"])
                except:
                    return
                if not e["welcomeMessage"] or e["welcomeMessage"] == "_default":
                    try:
                        await s.send(f"Welcome **{str(member)}** to {str(member.guild)}!")
                    except discord.Forbidden:
                        return
                else:
                    message = format_message(member, e["welcomeMessage"])
                    try:
                        await s.send(message)
                    except discord.Forbidden:
                        return
        except KeyError:
            return

def setup(bot):
    bot.add_cog(WelcomerListener(bot))
