import discord
from discord.ext import commands
import aiohttp
import datetime
import asyncio
import io
import io


class AnimalsCog(commands.Cog, name="Animal"):
    """Animal based commands"""

    def __init__(self, bot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.initialize())

    async def initialize(self):
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        self.task.cancel()
        self.session.close()

    @commands.command(aliases=["dog"], help="Returns a random image of a doggo")
    async def doggo(self, ctx):
        jsonResponse = {}
        doggoUrl = ""
        async with self.session.get('https://dog.ceo/api/breeds/image/random') as resp:
            jsonResponse = await resp.json()
        if jsonResponse["status"] != "success":
            await ctx.send("Error with the api, try again.")
        else:
            embed = discord.Embed(title="Doggo", description="")
            embed.set_image(url=jsonResponse["message"])
            await ctx.send(embed=embed)

    @commands.command(help="Returns a doggo with the given breed, usage `doggo <breed>`, you can find the breeds at https://dog.ceo/api/breeds/list/all")
    async def doggoBreed(self, ctx, arg=None):
        if arg == None:
            await ctx.send("No breed given!")
            return
        jsonResponse = {}

        async with self.session.get(f'https://dog.ceo/api/breed/{arg}/images/random') as resp:
            jsonResponse = await resp.json()
        if jsonResponse["status"] != "success":
            await ctx.send(jsonResponse["message"])
        else:
            embed = discord.Embed().set_image(url=jsonResponse["message"])
            await ctx.send(embed=embed)

    @commands.command(help="Returns a random image of a cat")
    async def cat(self, ctx):
        async with self.session.get('https://cataas.com/cat') as r:
            res = await r.read()
            embed = discord.Embed().set_image(url="attachment://pp.png")
            await ctx.send(file=discord.File(io.BytesIO(res), filename="pp.png"), embed=embed)

    @commands.command(help="Returns a random gif of a cat")
    async def catGif(self, ctx):
        async with self.session.get('https://cataas.com/cat/gif') as r:
            res = await r.read()
            embed = discord.Embed().set_image(url="attachment://pp.gif")
            await ctx.send(file=discord.File(io.BytesIO(res), filename="pp.gif"), embed=embed)

    @commands.command(help="Returns a random image of a panda")
    async def panda(self, ctx):
        async with self.session.get('https://some-random-api.ml/img/panda') as r:
            res = await r.json()
            embed = discord.Embed(title="Panda")
            embed.set_image(url=res['link'])
            await ctx.send(embed=embed)

    @commands.command(aliases=['bird'], help="Returns a random image of a bird")
    async def birb(self, ctx):
        async with self.session.get('https://some-random-api.ml/img/birb') as r:
            res = await r.json()
            embed = discord.Embed(title="Birb")
            embed.set_image(url=res['link'])
            await ctx.send(embed=embed)

    @commands.command(help="Returns a random image of a fox")
    async def fox(self, ctx):
        async with self.session.get('https://some-random-api.ml/img/fox') as r:
            res = await r.json()
            embed = discord.Embed(title="Fox")
            embed.set_image(url=res['link'])
            await ctx.send(embed=embed)

    @commands.command()
    async def duck(self, ctx):
        """Duck."""
        async with self.session.get('https://random-d.uk/api/v2/random') as r:
            res = await r.json()
            if 'url' not in list(res.keys()):
                return await ctx.send("An error occurred")
            await ctx.send(embed=discord.Embed(
                title="Duck",
            ).set_image(
                url=res['url']
            ))


def setup(bot):
    bot.add_cog(AnimalsCog(bot))
