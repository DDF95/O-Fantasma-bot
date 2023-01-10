import os
import sys
from configparser import ConfigParser
from pathlib import Path

import requests
from telegram import Update
from telegram.ext import ContextTypes


DIRECTORY = Path(__file__).absolute().parent

cfg = ConfigParser(interpolation=None)
cfg.read(f"{DIRECTORY}/config.ini")

BOT_TOKEN = cfg.get("bot", "bot_token")
IG_USER = cfg.get("bot", "ig_user")

BOT_ADMINS = [int(admin) for admin in cfg["bot_admins"].values()]

HOST = cfg.get("transmission", "host")
PORT = cfg.getint("transmission", "port")
USERNAME = cfg.get("transmission", "username")
PASSWORD = cfg.get("transmission", "password")


def is_bot_admin(user_id):
    if user_id in BOT_ADMINS:
        return True
    else:
        return False


async def restart_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Restarting...")
    args = sys.argv[:]
    args.insert(0, sys.executable)
    os.chdir(os.getcwd())
    os.execv(sys.executable, args)


async def file_in_limits(url) -> bool:
    info = requests.head(url)
    if ('mp4' in info.headers["Content-Type"]) and (int(info.headers["Content-Length"]) <= 20000000):
        return True

    if ('image' in info.headers["Content-Type"]) and (int(info.headers["Content-Length"]) <= 5000000):
        return True
    return False