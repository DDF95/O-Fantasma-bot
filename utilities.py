import os
import sys

import requests
from telegram import Update
from telegram.ext import ContextTypes

import config


def is_bot_admin(user_id):
    if user_id in config.BOT_ADMINS:
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