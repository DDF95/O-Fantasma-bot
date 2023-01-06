import os
from pathlib import Path
import sys

import requests
import speech_recognition as sr
from pydub import AudioSegment


directory = Path(__file__).absolute().parent


def restart():
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


def transcribe_voice(path):
    new_path = f"{directory}/file.wav"
    AudioSegment.from_file(path).export(new_path, format='wav')

    r = sr.Recognizer()
    with sr.AudioFile(new_path) as source:
        audio = r.record(source)
    os.remove(new_path)

    try:
        return r.recognize_google(audio, language="it-IT")
    except sr.UnknownValueError:
        return '<inaudible>'
