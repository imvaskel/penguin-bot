import discord
import asyncpg
import asyncio
import toml
from discord.ext import commands, ipc
import datetime as dt
import aiohttp


async def get_prefix(bot, message: discord.Message):
    prefix = 'p,'

    if message.content.startswith(('jsk', 'eval')) and message.author.id in bot.owner_ids and bot.user.id == 753037464599527485:
        return ""

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
        self.session = aiohttp.ClientSession()

        self.start_time = dt.datetime.now()

        self.config = toml.load('config.toml')

        self.ipc = ipc.Server(self, "localhost", 8765, self.config['default']['ipc_key'])
        self.load_extension("utils.ipc")

        self.db = self.loop.run_until_complete(
            asyncpg.connect(user=self.config['default']['db_user'], password=self.config['default']['db_password'],
                            database=self.config['default']['db_name'], host='127.0.0.1'))

        # Cache stuff
        self.stats = {}
        self.prefixes = {}
        self.cache = {}
        self.disabledCommands = []
        self.blacklistedUsers = []
        self.reactionRoleDict = self.loop.run_until_complete(
            self.cache_reactionroles())

        records = self.loop.run_until_complete(
            self.db.fetch("SELECT * FROM blacklist"))
        for i in records:
            self.blacklistedUsers.append(i["id"])

        records = self.loop.run_until_complete(
            self.db.fetch("SELECT * FROM guild_config"))
        self.prefixes = dict(self.loop.run_until_complete(
            self.db.fetch("SELECT id, prefix FROM guild_config")))

        for record in records:
            d = self.refresh_template(record)
            self.cache.update(d)

    async def on_ipc_ready(self):
        print("ipc ready")

    def refresh_template(self, record: asyncpg.Record):
        d = {
            record["id"]: {"prefix": record["prefix"], "autorole": record["autorole"],
                           "welcomeMessage": record["welcomemessage"], "welcomeEnabled": record["welcomeenabled"],
                           "welcomeId": record["welcomeid"], "logId": record['log_id']}
        }
        return d

    async def refresh_cache(self):
        records = await self.db.fetch("SELECT * FROM guild_config")
        for record in records:
            d = self.refresh_template(record)
            self.cache.update(d)

    async def cache_reactionroles(self):
        return dict(await self.db.fetch("SELECT msg_id, role_id FROM reaction_roles"))

    async def refresh_blacklist(self):
        records = await self.db.fetch("SELECT * FROM blacklist")
        self.blacklistedUsers = []
        for i in records:
            self.blacklistedUsers.append(i["id"])

    async def refresh_connection(self):
        await self.db.close()
        self.db = await asyncpg.connect(user=self.config['default']['db_user'],
                                        password=self.config['default']['db_password'],
                                        database=self.config['default']['db_name'], host='127.0.0.1')

    async def refresh_cache_for(self, guildId):
        record = await self.db.fetchrow("SELECT * FROM guild_config WHERE id = $1", guildId)
        self.cache.update(self.refresh_template(record))

    def get_announcement(self):
        with open('announcement.txt', 'r') as file:
            self.announcement = file.read()
