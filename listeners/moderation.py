import discord
from discord.ext import commands


class ModerationListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener('on_member_ban')
    async def on_ban(self, guild, user):
        return

    @commands.Cog.listener('on_member_unban')
    async def on_unban(self, guild, user):
        if logId := self.bot.cache[guild.id]['logId']:
            channel = guild.get_channel(logId)
            l = [f"User Name: {user.name}", f"User ID: {user.id}"]

            if guild.me.guild_permissions.view_audit_log:
                log = await guild.me.audit_logs(limit = 1).flatten()
                log = log[0]
                if log.action is discord.AuditLogAction.unban:
                    mod = log.user
                    l.append(f"Moderator: {mod} [{mod.id}]")
                    l.append(f"Reason \n{log[0].reason}")
            try:
                embed = discord.Embed(title = "User unbanned",
                                      description = "\n".join(l))
                await channel.send(embed = embed)
            except:
                return
        else:
            return



def setup(bot):
    bot.add_cog(ModerationListener(bot))
