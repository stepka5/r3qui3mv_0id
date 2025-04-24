#!/data/data/com.termux/files/usr/bin/bash
# Скрипт автозапуска UserBot

cd ~/userbot

# Проверка зависимостей
if ! [ -x "$(command -v python)" ]; then
    termux-notification -t "UserBot Error" -c "Python not installed" --icon error
    exit 1
fi

# Проверка сессии
if ! [ -f "userbot_session.session" ]; then
    termux-notification -t "UserBot Error" -c "Session file missing" --icon error
    exit 1
fi

# Проверка уже запущенного бота
if pgrep -f "python main.py" > /dev/null; then
    exit 0
fi

# Запуск бота
nohup python main.py >> userbot.log 2>&1 &
disown

termux-notification -t "UserBot" -c "Bot started successfully" --icon play
