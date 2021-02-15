import discord
from discord.ext import commands
from discord import Webhook, AsyncWebhookAdapter
from datetime import datetime
from contextlib import suppress

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener('on_message_delete')
    async def message_delete(self, message: discord.Message):

        try:
            cache = self.bot.cache[message.guild.id]
            if (id := cache.get('logId', None)) is not None:
                channel = self.bot.get_channel(id)

                if channel is None:
                    return

                with suppress(discord.Forbidden):

                    embed = discord.Embed(
                        title="Message Deleted",
                        description=("**Content**:"
                                     "\n"
                                     f"{message.content}"
                                     ),
                        timestamp=datetime.utcnow(),
                        color = 0x2F3136
                    )
                    embed.add_field(
                        name="Info:",
                        value=f"Channel : {message.channel.mention} \n"
                    )

                    embed.set_author(
                        name=str(message.author),
                                 icon_url = str(message.author.avatar_url)
                    )

                    if message.guild.me.guild_permissions.view_audit_log is True:
                        entry = (await message.guild.audit_logs(limit=1).flatten())[0]
                        if entry.action == discord.AuditLogAction.message_delete:
                            if entry.target == message.author:
                                embed.set_footer(
                                    text=f"Deleted by {entry.user}",
                                    icon_url=str(entry.user.avatar_url)
                                )

                    await channel.send(embed=embed)
        except Exception as e:
            pass

    @commands.Cog.listener('on_message_edit')
    async def message_edit(self, before, after):
        if before.author.bot is True:
            return

        try:
            cache = self.bot.cache[before.guild.id]
            if (id := cache.get('logId', None)) is not None:
                with suppress(discord.Forbidden):
                    channel = self.bot.get_channel(id)

                    if channel is None:
                        return

                    embed = discord.Embed(
                        color=0x2F3136,
                        timestamp=after.created_at
                    )
                    embed.add_field(
                        name="Before Content",
                        value=before.content
                    )
                    embed.add_field(
                        name="After Content",
                        value=after.content,
                        inline=False
                    )
                    embed.set_author(
                        name = str(before.author),
                        icon_url=str(before.author.avatar_url)
                    )

                    await channel.send(content= f"Message Edited in {after.channel.mention} ",
                                    embed=embed,
                                    )
        except Exception as e:
            pass

def setup(bot):
    bot.add_cog(LoggingCog(bot))
