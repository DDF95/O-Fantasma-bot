# O-Fantasma-bot

## Setup
1. Install the latest version of python-telegram-bot:
```
pip3 install -U python-telegram-bot
```


2. The other required packages can be installed with:
```
pip3 install instaloader SpeechRecognition pydub aiohttp
```


3. You can login to Instagram using InstaLoader. In terminal, write:
```
instaloader -l <Instagram username>
```
I suggest you don't use your personal Instagram account.


4. Put the generated session file in the same directory of `ofantasma.py`.


5. In `config.ini` put your bot token and your Instagram username.


7. You are ready to go! Start the bot using:
```
python3 ofantasma.py
```

## To-do
- download Facebook videos
- major code refactor
