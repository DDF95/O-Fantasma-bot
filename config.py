from configparser import ConfigParser
from pathlib import Path


main_directory = Path(__file__).absolute().parent

cfg = ConfigParser(interpolation=None)
cfg.read(f"{main_directory}/config.ini")

BOT_TOKEN = cfg.get("bot", "bot_token")
IG_USER = cfg.get("bot", "ig_user")

BOT_ADMINS = [int(admin) for admin in cfg["bot_admins"].values()]

HOST = cfg.get("transmission", "host")
PORT = cfg.getint("transmission", "port")
USERNAME = cfg.get("transmission", "username")
PASSWORD = cfg.get("transmission", "password")