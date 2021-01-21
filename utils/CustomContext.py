import discord
from discord.ext import commands
from datetime import datetime

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

    async def codeblock(self, text):
        """Makes the given text into a code block"""
        text = str(text)

        p = commands.Paginator()

        def split_string(string):
            return string[:1900], string[1900:]

        for entry in split_string(text):
            p.add_line(entry)

        for page in p.pages:
            await self.send(page)

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
