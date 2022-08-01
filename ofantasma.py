import logging
import os
import random
import uuid
from configparser import ConfigParser
from pathlib import Path

import instaloader
import requests
from telegram import (InlineQueryResultArticle, InlineQueryResultVideo,
                      InputMediaPhoto, InputMediaVideo,
                      InputTextMessageContent, Update, constants)
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          InlineQueryHandler, MessageHandler, filters)

from utilities import (file_in_limits, get_tiktok_username_id,
                       get_tiktok_video_infos, transcribe_voice)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

cfg = ConfigParser(interpolation=None)
config_file = Path(__file__).with_name('config.ini')
cfg.read(config_file)

BOT_TOKEN = cfg.get("bot", "bot_token")
USER = cfg.get("bot", "ig_user")

application = ApplicationBuilder().token(BOT_TOKEN).build()

directory = Path(__file__).absolute().parent

try:
    L = instaloader.Instaloader(dirname_pattern=f"{directory}/instagram/")
    L.load_session_from_file(USER, f"{directory}/session-{USER}")
except Exception as e:
    print(e)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.language_code == "it":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ti scarico lu tiktok. Fai /help se vuoi")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="I'll download your TikTok. Do /help if you want")


async def download_igstories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if context.args and len(context.args) == 1:
            username = context.args[0].replace("@", "")
            if update.message.from_user.language_code == "it":
                messaggio = await update.message.reply_text(f"Sto scaricando le storie di {username}...")
            else:
                messaggio = await update.message.reply_text(f"Downloading stories from {username}...")
            profile = L.check_profile_id(username)

            if profile.has_viewable_story:
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_DOCUMENT)

                for stories in L.get_stories([profile.userid]):
                    for item in stories.get_items():
                        if item.is_video:
                            url = item.video_url
                            username = item.owner_username
                            await update.message.reply_video(video=url, parse_mode='HTML', caption=f"@{username}")
                        else:
                            url = item.url
                            username = item.owner_username
                            await update.message.reply_photo(photo=url, parse_mode='HTML', caption=f"@{username}")
            else:
                if update.message.from_user.language_code == "it":
                    await update.message.reply_text(f"{username} non ha nessuna storia.")
                else:
                    await update.message.reply_text(f"{username} doesn't have any story.")
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=messaggio.message_id)

        elif context.args and len(context.args) == 2:
            username = context.args[0].replace("@", "")
            if update.message.from_user.language_code == "it":
                messaggio = await update.message.reply_text(f"Sto scaricando l'ultima storia di {username}...")
            else:
                messaggio = await update.message.reply_text(f"Downloading the latest story from {username}...")
            profile = L.check_profile_id(username)
            story_list = []

            if profile.has_viewable_story:
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_DOCUMENT)

                for stories in L.get_stories([profile.userid]):
                    for item in stories.get_items():
                        story_list.append(item)

                story = story_list[-1]
                if story.is_video:
                    url = story.video_url
                    username = story.owner_username
                    await update.message.reply_video(video=url, parse_mode='HTML', caption=f"@{username}")
                else:
                    url = story.url
                    username = story.owner_username
                    await update.message.reply_photo(photo=url, parse_mode='HTML', caption=f"@{username}")

            else:
                if update.message.from_user.language_code == "it":
                    await update.message.reply_text(f"{username} non ha nessuna storia.")
                else:
                    await update.message.reply_text(f"{username} doesn't have any story.")
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=messaggio.message_id)

        elif not context.args:
            if update.message.from_user.language_code == "it":
                await update.message.reply_text(text="Non hai specificato nessun username.\n\nEsempi:\n<code>/storie @theofficialmads</code>: scarica tutte le storie di @theofficialmads\n<code>/storie @theofficialmads last</code>: scarica solo l'ultima storia di @theofficialmads.", parse_mode='HTML')
            else:
                await update.message.reply_text(text="You didn't specify any username.\n\nExamples:\n<code>/stories @theofficialmads</code>: download all stories of @theofficialmads\n<code>/stories @theofficialmads last</code>: download only the latest story of @theofficialmads", parse_mode='HTML')

    except Exception as e:
        await update.message.reply_text(f"Errore: {e}")


async def link_downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message:
            if update.message.text.startswith(("https://vm.tiktok.com", "https://www.tiktok.com")):
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_VIDEO)

                url_infos = await get_tiktok_username_id(update.message.text)
                username = url_infos[0]
                video_id = url_infos[1]

                video_infos = await get_tiktok_video_infos(username, video_id)
                video_url = video_infos.get("video_url")
                caption = video_infos.get("caption")

                if await file_in_limits(video_url):
                    await update.message.reply_video(video=video_url, parse_mode='HTML', caption=caption)
                else:
                    if update.message.from_user.language_code == "it":
                        messaggio = await update.message.reply_text("Il video è più grande del solito, dammi qualche secondo ok")
                    else:
                        messaggio = await update.message.reply_text("The video is too big, give me a second ok")
                    filename = uuid.uuid4()
                    video_width = video_infos.get("width")
                    video_height = video_infos.get("height")
                    open(f"{directory}/{filename}.mp4",
                        "wb").write(requests.get(video_url).content)
                    await update.message.reply_video(
                        video=open(f'{directory}/{filename}.mp4', "rb"),
                        caption=caption,
                        parse_mode='HTML',
                        width=video_width,
                        height=video_height
                    )
                    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=messaggio.message_id)
                    os.remove(f"{directory}/{filename}.mp4")

            if update.message.text.startswith(("https://www.instagram.com/p/", "https://www.instagram.com/reel/")):
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_DOCUMENT)
                
                split_instagram_url = update.message.text.split("?")[0].split("/")
                shortcode = split_instagram_url[4]
                post = instaloader.Post.from_shortcode(L.context, shortcode)
                username = post.owner_username
                if post.caption:
                    if len(post.caption) > 200:
                        description = post.caption[:200] + "..."
                    else:
                        description = post.caption
                else:
                    description = ""

                if post.typename == "GraphImage": # commented out because Telegram already privides the single image
                    url = post.url
                    # await update.message.reply_photo(photo=url, parse_mode='HTML', caption=f"@{username}\n{description}")

                elif post.typename == "GraphVideo":
                    url = post.video_url
                    await update.message.reply_video(video=url, parse_mode='HTML', caption=f"@{username}\n{description}")

                elif post.typename == "GraphSidecar":
                    medialist = []
                    for p in post.get_sidecar_nodes():
                        if p.is_video:
                            medialist.append(
                                InputMediaVideo(
                                    media=p.video_url,
                                    caption=f"@{username}\n{description}",
                                    parse_mode='HTML'
                                )
                            )
                        else:
                            medialist.append(
                                InputMediaPhoto(
                                    media=p.display_url,
                                    caption=f"@{username}\n{description}",
                                    parse_mode='HTML'
                                )
                            )
                    await update.message.reply_media_group(media=medialist)
                    await update.message.reply_text(f"@{username}\n{description}")

            if update.message.text.startswith(("https://www.instagram.com/stories/", "https://instagram.com/stories/")):
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_DOCUMENT)
                
                split_instagram_url = update.message.text.split("?")[0].split("/")

                media_id = split_instagram_url[5]
                story = instaloader.StoryItem.from_mediaid(
                    L.context, int(media_id))

                if story.is_video:
                    url = story.video_url
                    username = story.owner_username
                    await update.message.reply_video(video=url, parse_mode='HTML', caption=f"@{username}")
                else:
                    url = story.url
                    username = story.owner_username
                    await update.message.reply_photo(photo=url, parse_mode='HTML', caption=f"@{username}")

    except Exception as e:
        print(e)


async def inline_tiktok_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return

    try:
        if query.startswith(("https://vm.tiktok.com", "https://www.tiktok.com")):
            url_infos = await get_tiktok_username_id(query)
            username = url_infos[0]
            video_id = url_infos[1]

            video_infos = await get_tiktok_video_infos(username, video_id)
            video_url = video_infos.get("video_url")
            caption = video_infos.get("caption")
            thumbnail = video_infos.get("thumbnail_url")
            
            results = []

            if await file_in_limits(video_url):
                results.append(
                    InlineQueryResultVideo(
                        id=str(uuid.uuid4()),
                        video_url=video_url,
                        mime_type="video/mp4",
                        thumb_url=thumbnail,
                        title=f"TikTok video by {username}",
                        caption=caption,
                        parse_mode="HTML"
                    )
                )
                await context.bot.answer_inline_query(update.inline_query.id, results)
            else:
                results.append(
                    InlineQueryResultArticle(
                        id=str(uuid.uuid4()),
                        title=f"TikTok video by {username}",
                        input_message_content=InputTextMessageContent(
                            f"The video is too big, but here's the direct link to view it in your browser: <a href='{video_url}'>link</a>\n\n{caption}",
                            parse_mode="HTML"
                        ),
                        description=caption
                    )
                )
                await context.bot.answer_inline_query(update.inline_query.id, results)
            return

    except Exception as e:
        print(e)


async def spongebob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.reply_to_message.text:
            text = update.message.reply_to_message.text
        elif update.message.reply_to_message.caption:
            text = update.message.reply_to_message.caption

        output_text = ""

        for char in text:
            if char.isalpha():
                if random.random() > 0.5:
                    output_text += char.upper()
                else:
                    output_text += char.lower()
            else:
                output_text += char

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            reply_to_message_id=update.message.reply_to_message.message_id,
            text=output_text
        )

    except Exception as e:
        if update.message.from_user.language_code == "it":
            await update.message.reply_text(f"No hai sbagliato...")
        else:
            await update.message.reply_text(f"You have failed...")


async def on_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.voice:
            file = await update.message.voice.get_file()
            path = await file.download()
            response = transcribe_voice(path)
            os.remove(path)
            if update.message.from_user.language_code == "it":
                await context.bot.send_message(update.message.chat.id, f"Trascrizione:\n{response}", reply_to_message_id=update.message.message_id)
            else:
                await context.bot.send_message(update.message.chat.id, f"Transcription:\n{response}", reply_to_message_id=update.message.message_id)
        elif update.message.video_note:
            file = await update.message.video_note.get_file()
            path = await file.download()
            response = transcribe_voice(path)
            os.remove(path)
            if update.message.from_user.language_code == "it":
                await context.bot.send_message(update.message.chat.id, f"Trascrizione:\n{response}", reply_to_message_id=update.message.message_id)
            else:
                await context.bot.send_message(update.message.chat.id, f"Transcription:\n{response}", reply_to_message_id=update.message.message_id)    
    except Exception as e:
        print(e)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.language_code == "it":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Questo bot può scaricare automaticamente i video da TikTok, e i post, reel e storie di Instagram. Inoltre, trascrive automaticamente i messaggi audio.\n\nComandi:\n• <code>/storie @theofficialmads</code>: scarica tutte le storie di @theofficialmads\n• <code>/storie @theofficialmads last</code>: scarica solo l'ultima storia di @theofficialmads.\n• <code>/spongebob</code>\n\nSource code: https://github.com/DDF95/O-Fantasma-bot", parse_mode="HTML")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="This bot can automatically download TikTok videos, and posts, reels and stories from Instagram. It also automatically transcribes audio messages.\n\nCommands:\n• <code>/stories @theofficialmads</code>: download all stories of @theofficialmads\n• <code>/stories @theofficialmads last</code>: download only the last story of @theofficialmads.\n• <code>/spongebob</code>\n\nSource code: https://github.com/DDF95/O-Fantasma-bot", parse_mode="HTML")


if __name__ == '__main__':
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler, 0)

    link_downloader_handler = MessageHandler(filters.TEXT, link_downloader)
    application.add_handler(link_downloader_handler)

    download_stories_handler = CommandHandler(('storie', "stories"), download_igstories)
    application.add_handler(download_stories_handler, 1)

    inline_tiktok_download_handler = InlineQueryHandler(inline_tiktok_download)
    application.add_handler(inline_tiktok_download_handler)

    spongebob_handler = CommandHandler('spongebob', spongebob)
    application.add_handler(spongebob_handler, 2)

    on_voice_message_handler = MessageHandler(filters.VOICE | filters.VIDEO_NOTE, on_voice_message)
    application.add_handler(on_voice_message_handler, 3)

    help_handler = CommandHandler('help', help)
    application.add_handler(help_handler, 4)

    application.run_polling()
