import os
from pathlib import Path
from urllib import parse

import requests
import speech_recognition as sr
from pydub import AudioSegment

directory = Path(__file__).absolute().parent

async def get_tiktok_video_infos(username: str, ID: str) -> dict:
    """
    Get Infos from the tiktok page and return a dict of relevant informations
    """

    infos = {}

    api_url = f"https://www.tiktok.com/node/share/video/{username}/{ID}"

    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36'}

    s = requests.Session()
    r = s.get(api_url, headers=headers)
    data = r.json()

    try:
        video_url = data["itemInfo"]["itemStruct"]["video"]["downloadAddr"]
        caption = f"<a href='https://www.tiktok.com/{username}'>{username}</a> (<a href='https://www.tiktok.com/{username}/video/{ID}'>link</a>)\n"
        caption += data["itemInfo"]["itemStruct"]["desc"]
        height = data["itemInfo"]["itemStruct"]["video"]["height"]
        width = data["itemInfo"]["itemStruct"]["video"]["width"]
        thumbnail_url = data["itemInfo"]["itemStruct"]["video"]["cover"]

        infos["username"] = username
        infos["video_id"] = ID
        infos["video_url"] = video_url
        infos["title"] = f"Tiktok Video from {username}"
        infos["caption"] = caption
        infos["thumbnail_url"] = thumbnail_url
        infos["height"] = height
        infos["width"] = width
        return infos
    except Exception as e:
        return None


async def get_tiktok_username_id(url):
    """
    Get the username and the video id from a tiktok url
    """
    purl = parse.urlparse(url)

    if purl.netloc == "vm.tiktok.com":
        tiktok_id = purl.path.split("/")[1]
        link = f"https://vm.tiktok.com/{tiktok_id}"
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36'}
        response = requests.get(link, headers=headers)

        info_list = requests.utils.unquote(response.url).split("?")[0].split("/")

        username = info_list[3]
        id = info_list[5]
    elif purl.netloc == 'www.tiktok.com':
        username = purl.path.split("/")[1]
        id = purl.path.split("/")[3]
        link = url
    else:
        raise RuntimeError
    return (username, id, link)


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