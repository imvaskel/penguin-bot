import discord
from discord.ext import commands
import aiohttp, datetime, asyncio, io, configparser, time
from collections import deque
from aiogoogletrans import Translator, LANGUAGES
from discord.ext.commands.cooldowns import BucketType
from asyncdagpi import Client, ImageFeatures
from discord.ext.commands.core import command
from jishaku import codeblocks


class FunCog(commands.Cog, name="Fun"):
    """ Commands that serve no use except for being fun. """

    def __init__(self, bot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.initialize())
        self.translator = Translator()

    async def initialize(self):
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        self.task.cancel()
        self.session.close()

    @commands.command(
        help="Astronomy Picture of the Day, returns the NASA astronomy picture of the day from their API, found at https://api.nasa.gov/. Use `YYYY-MM-DD` for a specific date. If the length of the explaniation is over 1024 chars, it does not add a caption.")
    async def apod(self, ctx, date=None):
        if date == None:
            url = f"https://api.nasa.gov/planetary/apod?api_key={self.bot.nasa_api}"
        elif date != "":
            url = f"https://api.nasa.gov/planetary/apod?date={date}&api_key={self.bot.nasa_api}"

        async with self.session.get(url) as r:
            res = await r.json()

            try:
                await ctx.send(res['msg'])

            except KeyError:

                embed = discord.Embed(title=f"Astronomy Picture of The Day | {res['title']}",
                                      description=f"{res['date']}")
                embed.set_image(url=res['url'])
                embed.set_footer(text=res['explanation'])
                await ctx.send(embed=embed)

    @commands.command(help="Returns a random gif of a pat")
    async def pat(self, ctx):
        async with self.session.get("https://some-random-api.ml/animu/pat") as r:
            res = await r.json()
            embed = discord.Embed(title="Pat")
            embed.set_image(url=res['link'])
            await ctx.send(embed=embed)

    @commands.command(help="Returns a random meme")
    async def meme(self, ctx):
        async with self.session.get("https://some-random-api.ml/meme") as r:
            res = await r.json()
            embed = discord.Embed(title=str(res['caption']))
            embed.set_image(url=res['image'])
            await ctx.send(embed=embed)

    @commands.command(help="Returns a post from the given subreddit\nUsage: reddit <subreddit>")
    async def reddit(self, ctx, subreddit):
        url = f"https://reddit.com/r/{subreddit}/random.json?limit=1"

        async with self.session.get(f"https://reddit.com/r/{subreddit}/random.json?limit=1") as r:
            res = await r.json()
            s = ""
            subredditDict = dict(res[0]['data']['children'][0]['data'])
            if subredditDict['over_18'] == True:
                await ctx.send("\U0001f51e This subreddit or post is NSFW, sorry!")
                return
            embed = discord.Embed(title=f"{subredditDict['title']} | {subredditDict['subreddit_name_prefixed']}",
                                  description=f"<:upvote:596577438461591562> {subredditDict['ups']}",
                                  url=f"https://reddit.com{subredditDict['permalink']}")

            if subredditDict['selftext'] != "":
                embed.add_field(name="Post Content:", value=subredditDict['selftext'])
            else:
                embed.set_image(url=subredditDict['url'])
            embed.set_footer(text=f"Author: {subredditDict['author']}")
            await ctx.send(embed=embed)

    @commands.command(help="Returns a random pikachu gif or image")
    async def pikachu(self, ctx):
        async with self.session.get('https://some-random-api.ml/img/pikachu') as r:
            res = await r.json()
            embed = discord.Embed(title="Pikachu")
            embed.set_image(url=res['link'])
            await ctx.send(embed=embed)

    @commands.command(help="Returns a random joke")
    async def joke(self, ctx):
        async with self.session.get('https://some-random-api.ml/joke') as r:
            res = await r.json()
            embed = discord.Embed(title="Joke", description=res['joke'])
            await ctx.send(embed=embed)

    @commands.command(
        help="Translates to a given language \nUsage: `translate <language> <text>`, you can find the languages with the command languages")
    async def translate(self, ctx, language, *, arg: str):
        try:
            translation = await self.bot.translator.translate(arg, dest=language)
            embed = discord.Embed(title="Translation", decription=translation.text)
            embed.set_footer(text=f"Translated to {language} with {translation.confidence}% confidence.")
            await ctx.send(embed=embed)
        except ValueError:
            await ctx.send(embed=discord.Embed(description="Invalid language, use `languages` to see them.",
                                               color=discord.Color.red()))

    @commands.command(help="Returns languages and their codes for usage in translation.")
    async def languages(self, ctx):
        embed = discord.Embed(title="Translation Languages")
        embed.set_footer(text=LANGUAGES)
        await ctx.send(embed=embed)

    @commands.command(help="Turns the data given into a qr code")
    async def qr(self, ctx, *, data):
        data = data.replace(" ", "+")
        embed = discord.Embed(title="QR Code", description=data)
        embed.set_image(url=f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={data}")
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command(help="Takes a screenshot of the webpage, it must be `https://url.whatever`", aliases=["ss"])
    async def screenshot(self, ctx, url):
        start = time.perf_counter()

        embed = discord.Embed(title=f"Screenshot of {url}", color=discord.Color.from_rgb(48, 162, 242))
        async with self.session.get(f'https://image.thum.io/get/width/1920/crop/675/maxAge/1/noanimate/{url}') as r:
            res = await r.read()
            embed.set_image(url="attachment://pp.png")
            end = time.perf_counter()
            embed.set_footer(text=f"Image fetched in {round((end - start) * 1000)} ms")
            await ctx.send(file=discord.File(io.BytesIO(res), filename="pp.png"), embed=embed)

    @commands.command(aliases=["quickpoll"])
    async def qp(self, ctx):
        """Makes a quick poll, which is just adding reactions to the original message"""
        await ctx.message.add_reaction("<:greentick:770685801297215488>")
        await ctx.message.add_reaction("<:redTick:775792645728895038>")

    @commands.command(aliases=["echo"])
    async def say(self, ctx, *, text):
        await ctx.send(embed=discord.Embed(description=text).set_footer(text=f"Requested by {str(ctx.author)}"))

    @commands.command()
    async def embed(self, ctx, embedCode):
        """Makes an embed from JSON, use https://embedbuilder.nadekobot.me/ to make it. You can use codeblocks and it will get the JSON from them."""
        embedCode = codeblocks.codeblock_converter(embedCode)
        embed = discord.Embed()
        try:
            embed = discord.Embed.from_dict(embedCode[0])
        except Exception as e:
            return await ctx.send(f"An error occurred, probably because the embed was invalid ``` {e} ```")
        await ctx.send(embed=embed)

    @commands.command()
    async def mystbin(self, ctx, language = "txt", *, code):
        """Pastes something to mystbin, `language` is optional, as this will just default to .txt or the given language of the code block. Also supports code block detection."""
        code = codeblocks.codeblock_converter(code)
        if code[0]: language = code[0]
        url = await self.bot.mystbin.post(code[1], syntax = language)
        await ctx.send(embed = discord.Embed(
            title = "Your mystb.in paste",
            description=str(url),
            timestamp=datetime.datetime.utcnow()
        ))

def setup(bot):
    bot.add_cog(FunCog(bot))