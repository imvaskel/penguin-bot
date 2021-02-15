import discord
from discord.ext import commands
from datetime import datetime
import asyncio

class PenguinContext(commands.Context):

    async def embed(self, *args, **kwargs):
        """Sends an embed with the args given"""
        title = kwargs.get('title')
        description = kwargs.get('description')
        color = kwargs.get('color', 0x36393E)
        timestamp = kwargs.get('timestamp', datetime.utcnow())
        url = kwargs.get("url", None)
        embed = discord.Embed(title=title, description=description, color=color, timestamp=timestamp, url=url)

        embed.set_footer(icon_url=str(self.author.avatar_url), text=f"Requested by {self.author}")

        await self.send(embed = embed)

    async def refresh_cache(self):
        """Refreshes the cache for the guild in the ctx object"""
        self.bot.cache.update(self.bot.refresh_template(await self.bot.db.fetchrow("SELECT * FROM guild_config WHERE id = $1", self.guild.id)))

    async def codeblock(self, text, **kwargs):
        """Makes the given text into a code block"""
        code = kwargs.get('language')

        text = str(text)

        await self.send(f"```{code or ''}\n {text} ```")

    async def send(self, content= None, *, tts=False, embed=None,
               file=None, files=None, delete_after=None,
               nonce=None, allowed_mentions=None, reference=None,
               mention_author=None):
        if content:
            for key, value in self.bot.config.items():
                content = content.replace(str(value), "[censored]")

        return await super().send(content=content, file=file, embed=embed,
                                  delete_after=delete_after, nonce=nonce,
                                  allowed_mentions=allowed_mentions, tts=tts)

    def cache(self):
        return self.bot.cache[self.guild.id]

    async def confirm(self, text = None, **kwargs) -> bool:
        """Uses wait_for to confirm, returns a bool"""
        reactions = ["<:redTick:775792645728895038>", "<:greentick:770685801297215488>"]
        msg = None
        if text is not None:
            msg = await self.send(text)
        elif kwargs.get('embed') is not None:
            msg = await self.send(embed = kwargs.get('embed'))
        else:
            raise commands.BadArgument("There was not a text or embed input.")

        for r in reactions:
            await msg.add_reaction(r)

        try:
            reaction, member = await self.bot.wait_for('reaction_add', check = (
                lambda r, u : r.message.id == msg.id and
                u.id == self.author.id and
                str(r) in reactions
            )
                , timeout = 30)
            return bool(reactions.index(str(reaction)))
        except asyncio.TimeoutError:
            await self.send("You did not confirm in time.")
            return False
