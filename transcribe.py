import os

import speech_recognition
from pydub import AudioSegment
from telegram import Update
from telegram.ext import ContextTypes

import config


def transcribe_voice(path):
    new_path = f"{config.main_directory}/file.wav"
    AudioSegment.from_file(path).export(new_path, format='wav')

    r = speech_recognition.Recognizer()
    with speech_recognition.AudioFile(new_path) as source:
        audio = r.record(source)
    os.remove(new_path)

    try:
        return r.recognize_google(audio, language="it-IT")
    except speech_recognition.UnknownValueError:
        return '<inaudible>'


async def on_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if "settings" not in context.chat_data or context.chat_data["settings"]["att"] == "✅":
            if update.message.voice:
                file = await update.message.voice.get_file()
                audio = await file.download_to_drive()
                response = transcribe_voice(audio)
                if update.message.from_user.language_code == "it":
                    await context.bot.send_message(update.message.chat.id, f"Trascrizione:\n{response}", reply_to_message_id=update.message.message_id)
                else:
                    await context.bot.send_message(update.message.chat.id, f"Transcription:\n{response}", reply_to_message_id=update.message.message_id)
                os.remove(audio)
            elif update.message.video_note:
                file = await update.message.video_note.get_file()
                audio = await file.download_to_drive()
                response = transcribe_voice(audio)
                if update.message.from_user.language_code == "it":
                    await context.bot.send_message(update.message.chat.id, f"Trascrizione:\n{response}", reply_to_message_id=update.message.message_id)
                else:
                    await context.bot.send_message(update.message.chat.id, f"Transcription:\n{response}", reply_to_message_id=update.message.message_id)
                os.remove(audio)
    except Exception as e:
        print(e)