import yt_dlp
from telegram import constants

from utilities import *


async def send_facebook_video(update, context):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_DOCUMENT)

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url=update.message.text, download=False)
    caption = f"{info['title']}"
    
    formats = []
    for f in info['formats']:
        if f['ext'] == 'mp4':
            formats.append(f)

    file_url = formats[-1]['url']

    if not await file_in_limits(file_url):
        file_url = formats[-2]['url']

    if await file_in_limits(file_url):
        await update.message.reply_video(video=file_url, caption=caption[:1000], parse_mode='HTML')

    else:
        if update.message.from_user.language_code == "it":
            await update.message.reply_html(f"Questo video è troppo grande e non posso caricarlo, ma se clicchi <a href='{file_url}'>qui</a> puoi guardarlo dal browser.")