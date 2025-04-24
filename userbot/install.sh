#!/data/data/com.termux/files/usr/bin/bash
# Полная автоматическая установка UserBot

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${YELLOW}Начинаем установку UserBot...${NC}"

# Обновление пакетов
echo -e "${YELLOW}Обновляю пакеты Termux...${NC}"
pkg update -y && pkg upgrade -y
pkg install -y python git wget

# Установка зависимостей
echo -e "${YELLOW}Устанавливаю зависимости Python...${NC}"
pip install telethon gitpython requests psutil

# Клонирование репозитория
echo -e "${YELLOW}Клонирую репозиторий бота...${NC}"
if [ -d "userbot" ]; then
    echo -e "${YELLOW}Директория уже существует, обновляю...${NC}"
    cd userbot
    git pull origin main
else
    git clone https://github.com/stepka5/r3qui3mv_0id.git userbot
    cd userbot
fi

# Настройка конфигурации
echo -e "${YELLOW}Настраиваю бота...${NC}"

# Запрос данных у пользователя
read -p "Введите API ID (получить на my.telegram.org): " api_id
read -p "Введите API HASH: " api_hash
read -p "Введите номер телефона (в формате +79998887766): " phone_number
read -p "Есть ли у вас двухфакторная аутентификация? (y/n): " has_2fa

if [ "$has_2fa" = "y" ]; then
    read -p "Введите пароль двухфакторной аутентификации: " password
fi

# Создание config.py
echo "API_ID = $api_id" > config.py
echo "API_HASH = \"$api_hash\"" >> config.py
echo "SESSION_NAME = \"userbot_session\"" >> config.py
echo "ADMINS = []" >> config.py
echo "LOG_CHAT = None" >> config.py

# Авторизация
echo -e "${YELLOW}Авторизуюсь в Telegram...${NC}"
python -c "
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import sys

api_id = $api_id
api_hash = '$api_hash'
phone = '$phone_number'
password = '$password' if '$has_fa' == 'y' else None

try:
    with TelegramClient(StringSession(), api_id, api_hash) as client:
        client.start(phone=phone, password=password)
        print('Авторизация успешна!')
        with open('userbot_session.session', 'w') as f:
            f.write(client.session.save())
except Exception as e:
    print(f'Ошибка авторизации: {e}')
    sys.exit(1)
"

# Настройка автозапуска
echo -e "${YELLOW}Настраиваю автозапуск...${NC}"
chmod +x termux_autostart.sh
mkdir -p ~/.termux/boot
cp termux_autostart.sh ~/.termux/boot/

# Завершение установки
echo -e "${GREEN}Установка завершена!${NC}"
echo -e "Для запуска бота:"
echo -e "1. Закройте и откройте Termux для автозапуска"
echo -e "ИЛИ"
echo -e "2. Введите вручную: cd ~/userbot && python main.py"

# Первый запуск
echo -e "${YELLOW}Запускаю бота впервые...${NC}"
python main.py &
disown
