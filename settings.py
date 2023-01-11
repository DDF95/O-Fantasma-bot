from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from transmission_torrent import get_torrent_list


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not "settings" in context.chat_data:
            context.chat_data["settings"] = {
                "tiktokv": "✅",
                "instagramp": "✅",
                "stories": "✅",
                "att": "✅",
                "spongebob": "✅",
                "facebookv": "✅",
            }

        if update.message.from_user.language_code == "it":
            close_button = "Chiudi impostazioni"
        else:
            close_button = "Close settings"

        keyboard = [
            [
                InlineKeyboardButton(f'TikTok videos: {context.chat_data["settings"]["tiktokv"]}', callback_data="tiktokv"),
                InlineKeyboardButton(f'FB videos: {context.chat_data["settings"]["facebookv"]}', callback_data="facebookv")
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
                f'{context.chat_data["settings"]["facebookv"]} - Autodownload dei video di Facebook\n'
                f'{context.chat_data["settings"]["instagramp"]} - Autodownload dei post di Instagram\n'
                f'{context.chat_data["settings"]["stories"]} - /storie\n'
                f'{context.chat_data["settings"]["att"]} - Trascrizione dei messaggi vocali\n'
                f'{context.chat_data["settings"]["spongebob"]} - /spongebob',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                f'{context.chat_data["settings"]["tiktokv"]} - Autodownload of TikTok videos\n'
                f'{context.chat_data["settings"]["facebookv"]} - Autodownload of Facebook videos\n'
                f'{context.chat_data["settings"]["instagramp"]} - Autodownload of Instagram posts\n'
                f'{context.chat_data["settings"]["stories"]} - /stories\n'
                f'{context.chat_data["settings"]["att"]} - Transcription of audio messages\n'
                f'{context.chat_data["settings"]["spongebob"]} - /spongebob',
                reply_markup=reply_markup
            )
    except Exception as e:
        print(e)


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
            
            elif query.data == "facebookv":
                if context.chat_data["settings"]["facebookv"] == "✅":
                    context.chat_data["settings"]["facebookv"] = "❌"
                else:
                    context.chat_data["settings"]["facebookv"] = "✅"
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
                    InlineKeyboardButton(f'TikTok videos: {context.chat_data["settings"]["tiktokv"]}', callback_data="tiktokv"),
                    InlineKeyboardButton(f'FB videos: {context.chat_data["settings"]["facebookv"]}', callback_data="facebookv")
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
                    f'{context.chat_data["settings"]["facebookv"]} - Autodownload dei video di Facebook\n'
                    f'{context.chat_data["settings"]["instagramp"]} - Autodownload dei post di Instagram\n'
                    f'{context.chat_data["settings"]["stories"]} - /storie\n'
                    f'{context.chat_data["settings"]["att"]} - Trascrizione dei messaggi vocali\n'
                    f'{context.chat_data["settings"]["spongebob"]} - /spongebob',
                    reply_markup=reply_markup
                )
            else:
                await query.message.edit_text(
                    f'{context.chat_data["settings"]["tiktokv"]} - Autodownload of TikTok videos\n'
                    f'{context.chat_data["settings"]["facebookv"]} - Autodownload of Facebook videos\n'
                    f'{context.chat_data["settings"]["instagramp"]} - Autodownload of Instagram posts\n'
                    f'{context.chat_data["settings"]["stories"]} - /stories\n'
                    f'{context.chat_data["settings"]["att"]} - Transcription of audio messages\n'
                    f'{context.chat_data["settings"]["spongebob"]} - /spongebob',
                    reply_markup=reply_markup
                )
    except Exception as e:
        print(e)