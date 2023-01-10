# O-Fantasma-bot

## Setup
1. Install the latest version of python-telegram-bot:
```
pip3 install -U python-telegram-bot
```


2. The other required packages can be installed with:
```
pip3 install requests instaloader SpeechRecognition pydub aiohttp yt-dlp requests-html
```


3. You can login to Instagram using InstaLoader. In terminal, write:
```
instaloader -l <Instagram username>
```
I suggest you don't use your personal Instagram account.


4. Put the generated session file in the same directory of `ofantasma.py`.


5. In `config.ini` put your bot token, your Instagram username, the admin user IDs and the Transmission parameters.


7. You are ready to go! Start the bot using:
```
python3 ofantasma.py
```

## To-do
- fix some Facebook videos apoearing empty on Telegram
- settings refactor
- add a function to check if the bot can send a message, based on settings
- don't load a .py file if the needed config parameters are not set
- if no bot token is set, ask for it in the terminal