#!/data/data/com.termux/files/usr/bin/bash
# Скрипт автозапуска

cd ~/userbot/userbot  # Важно: правильный путь

if pgrep -f "python main.py" > /dev/null; then
    exit 0
fi

nohup python main.py >> userbot.log 2>&1 &
disown
