#!/data/data/com.termux/files/usr/bin/bash
# Полная установка UserBot

REPO_URL="https://github.com/stepka5/r3qui3mv_0id.git"

echo "➤ Устанавливаю UserBot..."

# Обновление пакетов
pkg update -y && pkg upgrade -y
pkg install -y python git

# Установка зависимостей
pip install telethon gitpython requests psutil

# Клонирование репозитория
if [ -d "ReQuiemUserBot" ]; then
    echo "➤ Обновляю существующую копию..."
    cd ReQuiemUserBot
    git pull
else
    git clone $REPO_URL ReQuiemUserBot
    cd ReQuiemUserBot
fi

# Запрос данных
echo "➤ Настройка бота:"
read -p "Введите API ID: " api_id
read -p "Введите API HASH: " api_hash
read -p "Введите номер телефона: " phone
read -p "Есть ли 2FA пароль? (y/n): " has_2fa

if [ "$has_2fa" = "y" ]; then
    read -p "Введите 2FA пароль: " password
fi

# Создание конфига
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
    client.start(phone='$phone', password='$password' if '$has_2fa' == 'y' else None)
    with open('userbot_session.session', 'w') as f:
        f.write(client.session.save())
    print('✓ Успешная авторизация!')
"

# Настройка автозапуска
echo "➤ Настраиваю автозапуск..."
chmod +x termux_autostart.sh
mkdir -p ~/.termux/boot
cp termux_autostart.sh ~/.termux/boot/

# Первый запуск
echo "➤ Запускаю бота..."
cd ~/ReQuiemUserBot  # Переходим в корень проекта
nohup python main.py > userbot.log 2>&1 &
disown

echo "✓ Установка завершена!"
echo "Команды управления:"
echo ".stop - остановить"
echo ".restart - перезапустить"
echo ".update - обновить"
