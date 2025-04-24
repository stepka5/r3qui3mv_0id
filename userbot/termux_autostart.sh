#!/data/data/com.termux/files/usr/bin/bash
# Проверка зависимостей перед запуском
if ! [ -x "$(command -v python)" ]; then
    termux-notification -t "Ошибка UserBot" -c "Python не установлен" --icon "error"
    exit 1
fi

cd ~/userbot

# Проверка сессии
if ! [ -f "userbot_session.session" ]; then
    termux-notification -t "Ошибка UserBot" -c "Сессия не найдена" --icon "error"
    exit 1
fi

# Проверка уже запущенного бота
if pgrep -f "python main.py" > /dev/null; then
    exit 0
fi

# Запуск бота
nohup python main.py >> userbot.log 2>&1 &
disown

termux-notification -t "UserBot" -c "Бот успешно запущен" --icon "play"
