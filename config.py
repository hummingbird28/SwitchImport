from decouple import config

API_ID = config("API_ID", cast=int, default=0)
API_HASH = config("API_HASH", default="")
BOT_TOKEN = config("BOT_TOKEN", default="")

from typing import List, Dict
from telethon import TelegramClient
from telethon.tl.types import User

import logging
LOG = logging.getLogger("Bot")
_info = LOG.info

def info(*args):
    _info(" ".join(map(str, args)))

LOG.info = info

TASKS = {}
Downloads = {}

class CONFIG:
    ACCOUNT_ID = 0
    ACCOUNT: User = None
    BOTS: Dict[int, Dict[str, TelegramClient | Dict]] = {}

GLOBAL = {}
