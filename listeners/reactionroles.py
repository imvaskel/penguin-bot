import discord
from discord.ext import commands


class ReactionRolesListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if int(payload.message_id) in self.bot.reactionRoleDict and str(payload.emoji) == "\U00002705":
            guild = self.bot.get_guild(int(payload.guild_id))
            member = guild.get_member(int(payload.user_id))
            role = guild.get_role(
                self.bot.reactionRoleDict[int(payload.message_id)])
            await member.add_roles(role, reason="Reaction Role")
        else:
            return

def setup(bot):
    bot.add_cog(ReactionRolesListener(bot))
