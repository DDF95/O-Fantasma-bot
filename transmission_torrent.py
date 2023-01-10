from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from transmission_rpc import Client

from utilities import *


async def get_torrent_list():
    c = Client(host=HOST, port=PORT, username=USERNAME, password=PASSWORD)
    torrents = c.get_torrents()

    import datetime
    import time

    if len(torrents) == 0:
        all_torrents = "Non ci sono torrent in download."
        return all_torrents
    else:
        all_torrents = ""
        active_torrents = "Attivi nelle ultime 24 ore:\n\n"
        download_speed = 0
        upload_speed = 0

        for torrent in torrents:
            if torrent.rateDownload > 0: 
                all_torrents += "⚡️ "
            elif torrent.progress == 100:
                all_torrents += "🎊 "
            elif torrent.available == 0 and torrent.progress != 100:
                all_torrents += "😡 "
            elif torrent.available > 0 and torrent.progress != 100 and torrent.rateDownload == 0:
                all_torrents += "🦦 "
            torrent_name_fixed = torrent.name.replace(".", " ")

            if torrent.rateDownload /1024 > 1024:
                download_speed = f"{round(torrent.rateDownload / 1024 / 1024, 2)} MB/s"
            else:
                download_speed = f"{round(torrent.rateDownload / 1024, 2)} KB/s"
            if torrent.rateUpload /1024 > 1024:
                upload_speed = f"{round(torrent.rateUpload / 1024 / 1024, 2)} MB/s"
            else:
                upload_speed = f"{round(torrent.rateUpload / 1024, 2)} KB/s"

            all_torrents += f"`{torrent_name_fixed}`\n*{torrent.progress}% | ↓ {download_speed} | ↑ {upload_speed}*\n\n"

            last_activity = int(datetime.datetime.timestamp(torrent.date_active))

            if time.time() - last_activity < 86400:
                if torrent.rateDownload > 0:
                    active_torrents += "⚡️ "
                elif torrent.progress == 100:
                    active_torrents += "🎊 "
                elif torrent.available == 0 and torrent.progress != 100:
                    active_torrents += "😡 "
                elif torrent.available > 0 and torrent.progress != 100 and torrent.rateDownload == 0:
                    active_torrents += "🦦 "
                torrent_name_fixed = torrent.name.replace(".", " ")

                if torrent.rateDownload /1024 > 1024:
                    download_speed = f"{round(torrent.rateDownload / 1024 / 1024, 2)} MB/s"
                else:
                    download_speed = f"{round(torrent.rateDownload / 1024, 2)} KB/s"
                if torrent.rateUpload /1024 > 1024:
                    upload_speed = f"{round(torrent.rateUpload / 1024 / 1024, 2)} MB/s"
                else:
                    upload_speed = f"{round(torrent.rateUpload / 1024, 2)} KB/s"
                
                active_torrents += f"`{torrent_name_fixed}`\n*{torrent.progress}% | ↓ {download_speed} | ↑ {upload_speed}*\n\n"

        if active_torrents == "Attivi nelle ultime 24 ore:\n\n":
            active_torrents = "Non ci sono torrent attivi nelle ultime 24 ore."
                
        return all_torrents, active_torrents


async def view_torrents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_bot_admin(update.message.from_user.id):
        keyboard = [
            [
                InlineKeyboardButton("Refresh", callback_data="refresh"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        all_torrents, active_torrents = await get_torrent_list()

        if context.args and context.args[0] == "-a":
            await update.message.reply_text(active_torrents, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await update.message.reply_text(all_torrents, reply_markup=reply_markup, parse_mode="Markdown")
    

async def add_torrent(update, context):
    if is_bot_admin(update.message.from_user.id):
        magnet_url = update.message.text
        c = Client(host="localhost", port=9091, username="admin", password="Eddy95")
        torrent = c.add_torrent(magnet_url)
        await update.message.reply_text(f"ok ho messo a scaricare `{torrent.name}`.", parse_mode="Markdown")