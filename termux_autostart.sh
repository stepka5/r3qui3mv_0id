#!/data/data/com.termux/files/usr/bin/bash
# Скрипт автозапуска

cd ~/r3qui3mv_0id/userbot

if pgrep -f "python main.py" > /dev/null; then
    exit 0
fi

nohup python main.py >> userbot.log 2>&1 &
disown