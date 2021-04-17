import logging
import coloredlogs
import os

from utils.CustomBot import PenguinBot
from utils.CustomErrors import *

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_HIDE"] = "True"

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
coloredlogs.install(fmt="%(asctime)s | %(name)s | %(levelname)s > %(message)s")

bot = PenguinBot()

if __name__ == "__main__":
    bot.ipc.start()
    bot.run(bot.config['token'])
