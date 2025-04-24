#!/data/data/com.termux/files/usr/bin/bash
# Установщик UserBot с исправленными путями

REPO_URL="https://github.com/stepka5/r3qui3mv_0id.git"
INSTALL_DIR="$HOME/ReQuiemUserBot"

echo "➤ Установка UserBot..."

# Обновление пакетов
pkg update -y && pkg upgrade -y
pkg install -y python git termux-api

# Установка зависимостей
pip install telethon requests psutil

# Клонирование репозитория
if [ -d "$INSTALL_DIR" ]; then
    echo "➤ Обновляю существующую установку..."
    cd "$INSTALL_DIR"
    git pull
else
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR" || exit
fi

# Проверка необходимых файлов
if ! [ -f "main.py" ]; then
    echo "❌ Ошибка: main.py не найден!"
    exit 1
fi

if ! [ -f "termux_autostart.sh" ]; then
    echo "❌ Ошибка: termux_autostart.sh не найден!"
    exit 1
fi

# Настройка бота
echo "➤ Введите данные для авторизации:"
read -p "API ID: " api_id
read -p "API HASH: " api_hash
read -p "Номер телефона: " phone
read -p "2FA пароль (если есть, иначе нажмите Enter): " password

# Создание config.py
cat > config.py <<EOL
API_ID = $api_id
API_HASH = "$api_hash"
SESSION_NAME = "userbot_session"
ADMINS = []
LOG_CHAT = None
EOL

# Авторизация
echo "➤ Авторизация в Telegram..."
python -c "
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
print('Создаём сессию...')
with TelegramClient(StringSession(), $api_id, '$api_hash') as client:
    client.start(phone='$phone', password='$password' if '$password' else None)
    with open('userbot_session.session', 'w') as f:
        f.write(client.session.save())
    print('✓ Авторизация успешна!')
"

# Настройка автозапуска
echo "➤ Настройка автозапуска..."
chmod +x termux_autostart.sh
mkdir -p ~/.termux/boot
cp termux_autostart.sh ~/.termux/boot/

# Первый запуск
echo "➤ Запуск бота..."
cd "$INSTALL_DIR" || exit
nohup python main.py > userbot.log 2>&1 &
disown

echo "✓ Установка завершена!"
echo "Бот запущен. Для управления используйте:"
echo ".stop - остановить"
echo ".restart - перезапустить"
echo ".update - обновить"
