import discord, configparser, asyncpg, asyncio, toml
from discord.ext import commands
import datetime as dt

async def get_prefix(bot: commands.AutoShardedBot, message: discord.Message):
    prefix = 'p,'

    if not message.guild:
        return commands.when_mentioned_or(*prefix)(bot, message)

    else:
        if message.guild.id in bot.prefixes:
            return commands.when_mentioned_or(bot.prefixes[message.guild.id])(bot, message)
        elif not message.guild.id in bot.prefixes:
            return commands.when_mentioned_or(*prefix)(bot, message)

class PenguinBot(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(get_prefix, *args, **kwargs)
        
        self.loop = asyncio.get_event_loop()

        self.start_time = dt.datetime.now()

        self.config = toml.load('config.toml')

        self.db = self.loop.run_until_complete(asyncpg.connect(user=self.config['default']['db_user'], password=self.config['default']['db_password'], database=self.config['default']['db_name'], host='127.0.0.1'))

        # Cache stuff
        self.prefixes = {}
        self.cache = {}
        self.disabledCommands = []
        self.blacklistedUsers = []
        self.reactionRoleDict = self.loop.run_until_complete(self.cache_reactionroles())

        records = self.loop.run_until_complete(self.db.fetch("SELECT * FROM blacklist"))
        for i in records:
            self.blacklistedUsers.append(i["id"])

        records = self.loop.run_until_complete(self.db.fetch("SELECT * FROM guild_config"))
        self.prefixes = dict(self.loop.run_until_complete(self.db.fetch("SELECT id, prefix FROM guild_config")))

        for record in records:
            d = {
  record["id"]: {"prefix": record["prefix"], "autorole": record["autorole"], "welcomeMessage": record["welcomemessage"], "welcomeEnabled": record["welcomeenabled"], "welcomeId": record["welcomeid"]}}
            self.cache.update(d)

    async def refresh_cache(self):
        records = await self.db.fetch("SELECT * FROM guild_config")
        for record in records:
            d = {
  record["id"]: {"prefix": record["prefix"], "autorole": record["autorole"], "welcomeMessage": record["welcomemessage"], "welcomeEnabled": record["welcomeenabled"], "welcomeId": record["welcomeid"]}
}  
            self.cache.update(d)

    async def cache_reactionroles(self):
        return dict(await self.db.fetch("SELECT msg_id, role_id FROM reaction_roles"))

    async def refresh_blacklist(self):
        records = await self.db.fetch("SELECT * FROM blacklist")
        self.blacklistedUsers = []
        for i in records: self.blacklistedUsers.append(i["id"])

    async def refresh_connection(self):
        await self.db.close()
        self.db = await asyncpg.connect(user=self.config['default']['db_user'], password=self.config['default']['db_password'], database=self.config['default']['db_name'], host='127.0.0.1')