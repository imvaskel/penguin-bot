import discord
from discord.ext import commands
from asyncdagpi import Client, ImageFeatures
from PIL import Image, ImageFilter
from io import BytesIO

class Images(commands.Cog):
    """Image manipulation commands"""
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def invert(self, ctx, member: discord.Member = None):
        """Inverts the author or given members profile picture"""
        if member is None: member = ctx.author
        url = str(member.avatar_url_as(format="png", static_format="png", size=1024))
        try: img = await self.bot.dagpi_client.image_process(ImageFeatures.invert(), url)
        except Exception as e: return await ctx.send(f"``` \n {e} ```") 
        file = discord.File(fp=img.image,filename=f"colors.{img.format}")
        await ctx.send(embed=discord.Embed(color = 0x31A1F1).set_image(url=f"attachment://colors.{img.format}"),file=file)
    
    @commands.command()
    async def magik(self, ctx, member: discord.Member = None):
        """Magiks the author or given members profile picture"""
        if member is None: member = ctx.author
        url = str(member.avatar_url_as(format="png", static_format="png", size=1024))
        try: img = await self.bot.dagpi_client.image_process(ImageFeatures.magik(), url)
        except Exception as e: return await ctx.send(f"``` \n {e} ```")
        file = discord.File(fp=img.image,filename=f"colors.{img.format}")
        await ctx.send(embed=discord.Embed(color = 0x31A1F1).set_image(url=f"attachment://colors.{img.format}"),file=file)
    
    @commands.command()
    async def pixel(self, ctx, member: discord.Member = None):
        """Pixelates the author or given members profile picture"""
        if member is None: member = ctx.author
        url = str(member.avatar_url_as(format="png", static_format="png", size=1024))
        try: img = await self.bot.dagpi_client.image_process(ImageFeatures.pixel(), url)
        except Exception as e: return await ctx.send(f"``` \n {e} ```")
        file = discord.File(fp=img.image,filename=f"colors.{img.format}")
        await ctx.send(embed=discord.Embed(color = 0x31A1F1).set_image(url=f"attachment://colors.{img.format}"),file=file)
    
    @commands.command(aliases = ['colours'])
    async def colors(self, ctx, member: discord.Member = None):
        """Returns the colors of the author or given members profile picture"""
        if member is None: member = ctx.author
        url = str(member.avatar_url_as(format="png", static_format="png", size=1024))
        try: img = await self.bot.dagpi_client.image_process(ImageFeatures.colors(), url)
        except Exception as e: return await ctx.send(f"``` \n {e} ```")
        file = discord.File(fp=img.image,filename=f"colors.{img.format}")
        await ctx.send(embed=discord.Embed(color = 0x31A1F1).set_image(url=f"attachment://colors.{img.format}"),file=file)
    
    @commands.command()
    async def ascii(self, ctx, member: discord.Member = None):
        """Makes the author or given members profile picture ASCII:tm:"""
        if member is None: member = ctx.author
        url = str(member.avatar_url_as(format="png", static_format="png", size=1024))
        try: img = await self.bot.dagpi_client.image_process(ImageFeatures.ascii(), url)
        except Exception as e: return await ctx.send(f"``` \n {e} ```")
        file = discord.File(fp=img.image,filename=f"colors.{img.format}")
        await ctx.send(embed=discord.Embed(color = 0x31A1F1).set_image(url=f"attachment://colors.{img.format}"),file=file)

    @commands.command()
    async def obama(self, ctx, member: discord.Member = None):
        """Makes the obama self award meme, but with author or given users profile picture"""
        if member is None: member = ctx.author
        url = str(member.avatar_url_as(format="png", static_format="png", size=1024))
        try: img = await self.bot.dagpi_client.image_process(ImageFeatures.obama(), url)
        except Exception as e: return await ctx.send(f"``` \n {e} ```")
        file = discord.File(fp=img.image,filename=f"colors.{img.format}")
        await ctx.send(embed=discord.Embed(color = 0x31A1F1).set_image(url=f"attachment://colors.{img.format}"),file=file)
    
    @commands.command()
    async def flip(self, ctx, member: discord.Member = None):
        """Flips the avatar"""
        if not member: member = ctx.author
        avatarUrl = member.avatar_url_as(size = 512, format = "png")
        avatar = BytesIO(await avatarUrl.read())
        image = Image.open(avatar)
        
        image = image.rotate(180)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        await ctx.send(file = discord.File(buffer, filename = "flip.png"))
    
    @commands.command()
    async def blur(self, ctx, member: discord.Member = None):
        """Blurs the avatar"""
        if not member: member = ctx.author
        avatarUrl = member.avatar_url_as(size = 512, format = "png")
        avatar = BytesIO(await avatarUrl.read())
        image = Image.open(avatar)
        
        image = image.filter(ImageFilter.BLUR)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        await ctx.send(file = discord.File(buffer, filename = "blur.png"))

    @commands.command()
    async def sharpen(self, ctx, member: discord.Member = None):
        """Sharpens the avatar"""
        if not member: member = ctx.author
        avatarUrl = member.avatar_url_as(size = 512, format = "png")
        avatar = BytesIO(await avatarUrl.read())
        image = Image.open(avatar)
        
        image = image.filter(ImageFilter.SHARPEN)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        await ctx.send(file = discord.File(buffer, filename = "sharpen.png"))
    
    @commands.command()
    async def emboss(self, ctx, member: discord.Member = None):
        """Embosses the avatar"""
        if not member: member = ctx.author
        avatarUrl = member.avatar_url_as(size = 512, format = "png")
        avatar = BytesIO(await avatarUrl.read())
        image = Image.open(avatar)
        
        image = image.filter(ImageFilter.EMBOSS)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        await ctx.send(file = discord.File(buffer, filename = "emboss.png"))


        


def setup(bot):
    bot.add_cog(Images(bot))

