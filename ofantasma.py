import json
import logging
import os
import random
import uuid
from configparser import ConfigParser
from pathlib import Path

import instaloader
import requests
from telegram import (InlineQueryResultVideo, InputMediaPhoto, InputMediaVideo,
                      Update, constants)
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          InlineQueryHandler, MessageHandler, filters)

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
    L = instaloader.Instaloader()
    L.load_session_from_file(USER, f"{directory}/session-{USER}")

except Exception as e:
    print(e)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Ti scarico lu tiktok se mi invii il link"
    )


async def download_igstories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if context.args and len(context.args) == 1:
            username = context.args[0].replace("@", "")
            messaggio = await update.message.reply_text(f"Sto scaricando le storie di {username}...")
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
                await update.message.reply_text(f"{username} non ha nessuna storia.")

            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=messaggio.message_id)

        elif context.args and len(context.args) == 2:
            username = context.args[0].replace("@", "")
            messaggio = await update.message.reply_text(f"Sto scaricando l'ultima storia di {username}...")
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
                await update.message.reply_text(f"{username} non ha nessuna storia.")

            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=messaggio.message_id)

        elif not context.args:
            await update.message.reply_text(text="Non hai specificato nessun username.\n\nEsempi:\n<code>/storie @theofficialmads</code>: scarica tutte le storie di @theofficialmads\n<code>/storie @theofficialmads last</code>: scarica solo l'ultima storia di @theofficialmads.", parse_mode='HTML')

    except Exception as e:
        await update.message.reply_text(f"Errore: {e}")


async def link_downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.text.startswith("https://vm.tiktok.com"):
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_VIDEO)

            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36'}
            tiktok_url = requests.get(update.message.text, headers=headers)
            split_tiktok_url = tiktok_url.url.split("?")[0].split("/")

            tiktok_api_url = f"https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=[{split_tiktok_url[5]}]"
            tiktok_api_json = get_json_from_url(tiktok_api_url)
            tiktok_video_url = tiktok_api_json["aweme_details"][0]["video"]["play_addr"]["url_list"][0]
            tiktok_caption = tiktok_api_json["aweme_details"][0]["desc"]

            if await file_in_limits(tiktok_video_url):
                await update.message.reply_video(video=tiktok_video_url, caption=f"{split_tiktok_url[3]}\n{tiktok_caption}", parse_mode='HTML')
            else:
                messaggio = await update.message.reply_text("Il video è più grande del solito, dammi qualche secondo ok")
                video_id = uuid.uuid4()
                video_width = tiktok_api_json["aweme_details"][0]["video"]["width"]
                video_height = tiktok_api_json["aweme_details"][0]["video"]["height"]
                open(f"{directory}/{video_id}.mp4",
                     "wb").write(requests.get(tiktok_video_url).content)
                await update.message.reply_video(
                    video=open(f'{directory}/{video_id}.mp4', "rb"),
                    caption=f"{split_tiktok_url[3]}\n{tiktok_caption}",
                    parse_mode='HTML',
                    width=video_width,
                    height=video_height
                )
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=messaggio.message_id)
                os.remove(f"{directory}/{video_id}.mp4")

        if update.message.text.startswith("https://www.tiktok.com"):
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_VIDEO)

            split_tiktok_url = update.message.text.split("?")[0].split("/")

            tiktok_api_url = f"https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=[{split_tiktok_url[5]}]"
            tiktok_api_json = get_json_from_url(tiktok_api_url)
            tiktok_video_url = tiktok_api_json["aweme_details"][0]["video"]["play_addr"]["url_list"][0]
            tiktok_caption = tiktok_api_json["aweme_details"][0]["desc"]

            if await file_in_limits(tiktok_video_url):
                await update.message.reply_video(video=tiktok_video_url, caption=f"{split_tiktok_url[3]}\n{tiktok_caption}", parse_mode='HTML')
            else:
                messaggio = await update.message.reply_text("Il video è più grande del solito, dammi qualche secondo ok")
                video_id = uuid.uuid4()
                video_width = tiktok_api_json["aweme_details"][0]["video"]["width"]
                video_height = tiktok_api_json["aweme_details"][0]["video"]["height"]
                open(f"{directory}/{video_id}.mp4",
                     "wb").write(requests.get(tiktok_video_url).content)
                await update.message.reply_video(
                    video=open(f'{directory}/{video_id}.mp4', "rb"),
                    caption=f"{split_tiktok_url[3]}\n{tiktok_caption}",
                    parse_mode='HTML',
                    width=video_width,
                    height=video_height
                )
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=messaggio.message_id)
                os.remove(f"{directory}/{video_id}.mp4")

        if update.message.text.startswith("https://www.instagram.com/p/") or update.message.text.startswith("https://www.instagram.com/reel/"):
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

            if post.typename == "GraphImage":
                url = post.url
                await update.message.reply_photo(photo=url, parse_mode='HTML', caption=f"@{username}\n{description}")

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

        if update.message.text.startswith("https://www.instagram.com/stories/") or update.message.text.startswith("https://instagram.com/stories/"):
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
        # await update.message.reply_text(f"Errore: {e}")
        print(e)


async def inline_tiktok_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return

    try:
        if query.startswith("https://vm.tiktok.com"):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36'}
            tiktok_url = requests.get(query, headers=headers)
            split_tiktok_url = tiktok_url.url.split("?")[0].split("/")

            tiktok_api_url = f"https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=[{split_tiktok_url[5]}]"
            tiktok_api_json = get_json_from_url(tiktok_api_url)
            tiktok_video_url = tiktok_api_json["aweme_details"][0]["video"]["play_addr"]["url_list"][0]
            tiktok_thumbnail_url = tiktok_api_json["aweme_details"][0]["video"]["cover"]["url_list"][0]
            tiktok_caption = tiktok_api_json["aweme_details"][0]["desc"]

            results = []
            results.append(
                InlineQueryResultVideo(
                    id=str(uuid.uuid4()),
                    video_url=tiktok_video_url,
                    mime_type="video/mp4",
                    thumb_url=tiktok_thumbnail_url,
                    title=f"TikTok di {split_tiktok_url[3]}",
                    caption=f"{split_tiktok_url[3]}\n{tiktok_caption}",
                    parse_mode="HTML"
                )
            )
            await context.bot.answer_inline_query(update.inline_query.id, results)
            return

        if query.startswith("https://www.tiktok.com"):
            split_tiktok_url = query.split("?")[0].split("/")

            tiktok_api_url = f"https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=[{split_tiktok_url[5]}]"
            tiktok_api_json = get_json_from_url(tiktok_api_url)
            tiktok_video_url = tiktok_api_json["aweme_details"][0]["video"]["play_addr"]["url_list"][0]
            tiktok_thumbnail_url = tiktok_api_json["aweme_details"][0]["video"]["cover"]["url_list"][0]
            tiktok_caption = tiktok_api_json["aweme_details"][0]["desc"]

            results = []
            results.append(
                InlineQueryResultVideo(
                    id=str(uuid.uuid4()),
                    video_url=tiktok_video_url,
                    mime_type="video/mp4",
                    thumb_url=tiktok_thumbnail_url,
                    title=f"TikTok di {split_tiktok_url[3]}",
                    caption=f"{split_tiktok_url[3]}\n{tiktok_caption}",
                    parse_mode="HTML"
                )
            )
            await context.bot.answer_inline_query(update.inline_query.id, results)
            return

    except Exception as e:
        await update.message.reply_text(f"Errore: {e}")


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
        await update.message.reply_text(f"No hai sbagliato...")


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


async def file_in_limits(url) -> bool:
    info = requests.head(url)
    if ('mp4' in info.headers["Content-Type"]) and (int(info.headers["Content-Length"]) <= 20000000):
        return True

    if ('image' in info.headers["Content-Type"]) and (int(info.headers["Content-Length"]) <= 5000000):
        return True
    return False


if __name__ == '__main__':
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler, 0)

    link_downloader_handler = MessageHandler(filters.TEXT, link_downloader)
    application.add_handler(link_downloader_handler)

    download_stories_handler = CommandHandler('storie', download_igstories)
    application.add_handler(download_stories_handler, 1)

    inline_tiktok_download_handler = InlineQueryHandler(inline_tiktok_download)
    application.add_handler(inline_tiktok_download_handler)

    spongebob_handler = CommandHandler('spongebob', spongebob)
    application.add_handler(spongebob_handler, 2)

    application.run_polling()
