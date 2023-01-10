import logging
import os
import random

import instaloader
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      InputMediaPhoto, InputMediaVideo, Update, constants)
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          CommandHandler, ContextTypes, InlineQueryHandler,
                          MessageHandler, PicklePersistence, filters)

from facebook import *
from tiktok import *
from transcribe import *
from transmission_torrent import *
from utilities import *


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if not os.path.exists(f"{DIRECTORY}/db"):
    os.makedirs(f"{DIRECTORY}/db")

persistence = PicklePersistence(filepath=f'{DIRECTORY}/db/persistence.pkl')

application = ApplicationBuilder().token(BOT_TOKEN).persistence(persistence).build()

try:
    L = instaloader.Instaloader(dirname_pattern=f"{DIRECTORY}/instagram/", iphone_support=False, save_metadata=False)
    L.load_session_from_file(IG_USER, f"{DIRECTORY}/session-{IG_USER}")
except Exception as e:
    print(e)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.language_code == "it":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ti scarico lu tiktok. Fai /help se vuoi")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="I'll download your TikTok. Do /help if you want")


async def download_igstories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if "settings" not in context.chat_data or context.chat_data["settings"]["stories"] == "✅":
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
                    await update.message.reply_text(text="You didn't specify any username.\n\nExamples:\n<code>/stories @theofficialmads</code>: download all the stories of @theofficialmads\n<code>/stories @theofficialmads last</code>: download only the last story of @theofficialmads", parse_mode='HTML')

    except Exception as e:
        await update.message.reply_text(f"Errore: {e}")


async def link_downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        if update.message.text.startswith(("https://vm.tiktok.com", "https://www.tiktok.com")):
            if "settings" not in context.chat_data or context.chat_data["settings"]["tiktokv"] == "✅":
                await send_tiktok_video(update, context)

        if update.message.text.startswith(("https://www.instagram.com/p/", "https://www.instagram.com/reel/")):
            if "settings" not in context.chat_data or context.chat_data["settings"]["instagramp"] == "✅":
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

        if update.message.text.startswith(("https://www.instagram.com/stories/", "https://instagram.com/stories/")):
            if "settings" not in context.chat_data or context.chat_data["settings"]["instagramp"] == "✅":
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

        if update.message.text.startswith(("magnet:", "https://proxyrarbg.org/download.php")):
            await add_torrent(update, context)
        
        if update.message.text.startswith(("https://fb.watch/", "https://www.facebook.com/reel/")):
            await send_facebook_video(update, context)


async def spongebob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if "settings" not in context.chat_data or context.chat_data["settings"]["spongebob"] == "✅":
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

    except Exception:
        pass


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.language_code == "it":
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="Questo bot può scaricare automaticamente i video da TikTok, e i post, reel e storie di Instagram. Inoltre, trascrive automaticamente i messaggi audio."
            "\n\nComandi:"
            "\n• <code>/impostazioni</code>: attiva o disattiva le funzioni del bot."
            "\n• <code>/storie @theofficialmads</code>: scarica tutte le storie di @theofficialmads."
            "\n• <code>/storie @theofficialmads last</code>: scarica solo l'ultima storia di @theofficialmads."
            "\n• <code>/spongebob</code>: usa questo comando in risposta ad un messaggio."
            "\n\nSource code: https://github.com/DDF95/O-Fantasma-bot", 
            parse_mode="HTML"
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="This bot can automatically download TikTok videos, and Instagram posts, reels and stories. It also automatically transcribes audio messages."
            "\n\nCommands:"
            "\n• <code>/settings</code>: enable or disable the bot's functionalities."
            "\n• <code>/stories @theofficialmads</code>: download all the stories of @theofficialmads."
            "\n• <code>/stories @theofficialmads last</code>: download only the last story of @theofficialmads."
            "\n• <code>/spongebob</code>: use this command in reply to a message."
            "\n\nSource code: https://github.com/DDF95/O-Fantasma-bot", 
            parse_mode="HTML"
        )


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not "settings" in context.chat_data:
            context.chat_data["settings"] = {
                "tiktokv": "✅",
                "instagramp": "✅",
                "stories": "✅",
                "att": "✅",
                "spongebob": "✅",
            }

        if update.message.from_user.language_code == "it":
            close_button = "Chiudi impostazioni"
        else:
            close_button = "Close settings"

        keyboard = [
            [
                InlineKeyboardButton(f'TikTok videos: {context.chat_data["settings"]["tiktokv"]}', callback_data="tiktokv") 
            ],
            [
                InlineKeyboardButton(f'IG posts: {context.chat_data["settings"]["instagramp"]}', callback_data="instagramp"), 
                InlineKeyboardButton(f'/stories: {context.chat_data["settings"]["stories"]}', callback_data="stories")
            ],
            [
                InlineKeyboardButton(f'Audio to text: {context.chat_data["settings"]["att"]}', callback_data="att"), 
                InlineKeyboardButton(f'/spongebob: {context.chat_data["settings"]["spongebob"]}', callback_data="spongebob")
            ],
            [
                InlineKeyboardButton(close_button, callback_data="close")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.message.from_user.language_code == "it":
            await update.message.reply_text(
                f'{context.chat_data["settings"]["tiktokv"]} - Autodownload dei video di TikTok\n'
                f'{context.chat_data["settings"]["instagramp"]} - Autodownload dei post di Instagram\n'
                f'{context.chat_data["settings"]["stories"]} - /storie\n'
                f'{context.chat_data["settings"]["att"]} - Trascrizione dei messaggi vocali\n'
                f'{context.chat_data["settings"]["spongebob"]} - /spongebob',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                f'{context.chat_data["settings"]["tiktokv"]} - Autodownload of TikTok videos\n'
                f'{context.chat_data["settings"]["instagramp"]} - Autodownload of Instagram posts\n'
                f'{context.chat_data["settings"]["stories"]} - /stories\n'
                f'{context.chat_data["settings"]["att"]} - Transcription of audio messages\n'
                f'{context.chat_data["settings"]["spongebob"]} - /spongebob',
                reply_markup=reply_markup
            )
    except Exception as e:
        print(e)


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.reply_to_message.message_id)


async def settings_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        query = update.callback_query

        if query.data == "close":
            await query.message.delete()
            if query.from_user.language_code == "it":
                await query.answer(f"Impostazioni chiuse.")
            else:
                await query.answer(f"Settings closed.")
        
        elif query.data == "refresh":
            keyboard = [
                [
                    InlineKeyboardButton("Refresh", callback_data="refresh"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            all_torrents, active_torrents = await get_torrent_list()

            if query.message.text.startswith("Attivi"):
                await query.message.edit_text(active_torrents, reply_markup=reply_markup, parse_mode="Markdown")
            else:
                await query.message.edit_text(all_torrents, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            if query.data == "tiktokv":
                if context.chat_data["settings"]["tiktokv"] == "✅":
                    context.chat_data["settings"]["tiktokv"] = "❌"
                else:
                    context.chat_data["settings"]["tiktokv"] = "✅"
                if query.from_user.language_code == "it":
                    await query.answer(f"Impostazioni salvate.")
                else:
                    await query.answer(f"Settings saved.")
            
            elif query.data == "instagramp":
                if context.chat_data["settings"]["instagramp"] == "✅":
                    context.chat_data["settings"]["instagramp"] = "❌"
                else:
                    context.chat_data["settings"]["instagramp"] = "✅"
                if query.from_user.language_code == "it":
                    await query.answer(f"Impostazioni salvate.")
                else:
                    await query.answer(f"Settings saved.")
            
            elif query.data == "stories":
                if context.chat_data["settings"]["stories"] == "✅":
                    context.chat_data["settings"]["stories"] = "❌"
                else:
                    context.chat_data["settings"]["stories"] = "✅"
                if query.from_user.language_code == "it":
                    await query.answer(f"Impostazioni salvate.")
                else:
                    await query.answer(f"Settings saved.")
            
            elif query.data == "att":
                if context.chat_data["settings"]["att"] == "✅":
                    context.chat_data["settings"]["att"] = "❌"
                else:
                    context.chat_data["settings"]["att"] = "✅"
                if query.from_user.language_code == "it":
                    await query.answer(f"Impostazioni salvate.")
                else:
                    await query.answer(f"Settings saved.")
            
            elif query.data == "spongebob":
                if context.chat_data["settings"]["spongebob"] == "✅":
                    context.chat_data["settings"]["spongebob"] = "❌"
                else:
                    context.chat_data["settings"]["spongebob"] = "✅"
                if query.from_user.language_code == "it":
                    await query.answer(f"Impostazioni salvate.")
                else:
                    await query.answer(f"Settings saved.")

            if query.from_user.language_code == "it":
                close_button = "Chiudi impostazioni"
            else:
                close_button = "Close settings"

            keyboard = [
                [
                    InlineKeyboardButton(f'TikTok videos: {context.chat_data["settings"]["tiktokv"]}', callback_data="tiktokv")
                ],
                [
                    InlineKeyboardButton(f'IG posts: {context.chat_data["settings"]["instagramp"]}', callback_data="instagramp"), 
                    InlineKeyboardButton(f'/stories: {context.chat_data["settings"]["stories"]}', callback_data="stories")
                ],
                [
                    InlineKeyboardButton(f'Audio to text: {context.chat_data["settings"]["att"]}', callback_data="att"), 
                    InlineKeyboardButton(f'/spongebob: {context.chat_data["settings"]["spongebob"]}', callback_data="spongebob")
                ],
                [
                    InlineKeyboardButton(close_button, callback_data="close")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if query.from_user.language_code == "it":
                await query.message.edit_text(
                    f'{context.chat_data["settings"]["tiktokv"]} - Autodownload dei video di TikTok\n'
                    f'{context.chat_data["settings"]["instagramp"]} - Autodownload dei post di Instagram\n'
                    f'{context.chat_data["settings"]["stories"]} - /storie\n'
                    f'{context.chat_data["settings"]["att"]} - Trascrizione dei messaggi vocali\n'
                    f'{context.chat_data["settings"]["spongebob"]} - /spongebob',
                    reply_markup=reply_markup
                )
            else:
                await query.message.edit_text(
                    f'{context.chat_data["settings"]["tiktokv"]} - Autodownload of TikTok videos\n'
                    f'{context.chat_data["settings"]["instagramp"]} - Autodownload of Instagram posts\n'
                    f'{context.chat_data["settings"]["stories"]} - /stories\n'
                    f'{context.chat_data["settings"]["att"]} - Transcription of audio messages\n'
                    f'{context.chat_data["settings"]["spongebob"]} - /spongebob',
                    reply_markup=reply_markup
                )
    except Exception as e:
        print(e)


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

    settings_handler = CommandHandler(('settings', 'impostazioni'), settings)
    application.add_handler(settings_handler, 5)

    settings_button_handler = CallbackQueryHandler(settings_button)
    application.add_handler(settings_button_handler, 6)

    delete_handler = CommandHandler("delete", delete)
    application.add_handler(delete_handler, 7) 

    view_torrents_handler = CommandHandler("torrent", view_torrents)
    application.add_handler(view_torrents_handler, 8)

    restart_bot_handler = CommandHandler("restart", restart_bot)
    application.add_handler(restart_bot_handler, 9)

    application.run_polling(drop_pending_updates=True)
