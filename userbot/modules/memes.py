import asyncio
import random
import logging
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetHistoryRequest

logger = logging.getLogger(__name__)

class MemesModule:
    def __init__(self, bot):
        self.bot = bot
        self.channels = {
            "шутка": "@shutkimemes",
            "жоскиймем": "@joskiimems", 
            "смешноймем": "@smeshnoymems",
            "смехуятина": "@smehuatinka",
            "анекдот": "@anekdotsmemes",
            "кружок": "@ponnnnnit"
        }
        self.channel_entities = {}
        self.memes_cache = {}
        self.circles_cache = []
        
        # Регистрируем команды сразу
        self.register_commands()
        
        # Откладываем инициализацию данных до подключения
        asyncio.create_task(self.initialize_after_connect())

    def register_commands(self):
        """Регистрация всех команд"""
        commands = {
            "шутка": ("Случайная шутка", self.joke_cmd),
            "жоскиймем": ("Жесткий мем", self.hard_meme_cmd),
            "смешноймем": ("Смешной мем", self.funny_meme_cmd),
            "смехуятина": ("Смешная всячина", self.funny_stuff_cmd),
            "анекдот": ("Случайный анекдот", self.anecdote_cmd),
            "кружок": ("Случайный кружок", self.circle_cmd),
            "мемлист": ("Статистика мемов", self.memelist_cmd),
            "обновитькеш": ("Обновить кеш мемов", self.update_cache_cmd)
        }
        
        for cmd, (desc, handler) in commands.items():
            self.bot.register_command(cmd, handler, desc)

    async def initialize_after_connect(self):
        """Инициализация после подключения к Telegram"""
        await self.bot.client.connect()  # Ждем подключения
        
        logger.info("Инициализация модуля Memes...")
        await self.load_channel_entities()
        await self.cache_messages()
        logger.info("Модуль Memes готов к работе")

    async def load_channel_entities(self):
        """Загрузка информации о каналах"""
        tasks = []
        for name, username in self.channels.items():
            tasks.append(self.get_channel_entity(username))
        
        results = await asyncio.gather(*tasks)
        
        for i, (name, _) in enumerate(self.channels.items()):
            if results[i]:
                self.channel_entities[name] = results[i]
                logger.info(f"Загружен канал: {name}")

    async def get_channel_entity(self, username):
        """Получение entity канала"""
        try:
            channel = await self.bot.client(GetFullChannelRequest(username))
            return channel.chats[0]
        except Exception as e:
            logger.error(f"Ошибка загрузки канала {username}: {e}")
            return None

    async def cache_messages(self):
        """Кеширование сообщений из каналов"""
        tasks = []
        for name, entity in self.channel_entities.items():
            if name == "кружок":
                tasks.append(self.get_circles(entity))
            else:
                tasks.append(self.get_channel_messages(entity))
        
        results = await asyncio.gather(*tasks)
        
        for i, name in enumerate(self.channel_entities):
            if name == "кружок":
                self.circles_cache = results[i]
            else:
                self.memes_cache[name] = results[i]
            logger.info(f"Загружено {len(results[i])} постов из {name}")

    async def get_channel_messages(self, entity):
        """Получение сообщений из канала"""
        try:
            messages = []
            async for message in self.bot.client.iter_messages(entity, limit=200):
                if message.text or message.media:
                    messages.append(message)
            return messages
        except Exception as e:
            logger.error(f"Ошибка получения сообщений: {e}")
            return []

    async def get_circles(self, entity):
        """Получение кружков (видео-заметок)"""
        try:
            circles = []
            async for message in self.bot.client.iter_messages(entity, limit=100):
                if message.video_note:
                    circles.append(message)
            return circles
        except Exception as e:
            logger.error(f"Ошибка получения кружков: {e}")
            return []

    async def send_random_post(self, event, category):
        """Отправка случайного поста"""
        if category not in self.memes_cache or not self.memes_cache[category]:
            await event.edit("😕 Нет доступных постов")
            return
            
        post = random.choice(self.memes_cache[category])
        await self.bot.client.send_message(
            event.chat_id,
            post.text or "📦 Мем",
            file=post.media,
            reply_to=event.reply_to_msg_id
        )
        await event.delete()

    async def send_random_circle(self, event):
        """Отправка случайного кружка"""
        if not self.circles_cache:
            await event.edit("😕 Нет доступных кружков")
            return
            
        circle = random.choice(self.circles_cache)
        await self.bot.client.send_message(
            event.chat_id,
            file=circle.video_note,
            reply_to=event.reply_to_msg_id
        )
        await event.delete()

    # Обработчики команд
    async def joke_cmd(self, event):
        await self.send_random_post(event, "шутка")

    async def hard_meme_cmd(self, event):
        await self.send_random_post(event, "жоскиймем")

    async def funny_meme_cmd(self, event):
        await self.send_random_post(event, "смешноймем")

    async def funny_stuff_cmd(self, event):
        await self.send_random_post(event, "смехуятина")

    async def anecdote_cmd(self, event):
        await self.send_random_post(event, "анекдот")

    async def circle_cmd(self, event):
        await self.send_random_circle(event)

    async def memelist_cmd(self, event):
        """Статистика мемов"""
        stats = "\n".join(
            f"{name}: {len(posts)}" 
            for name, posts in self.memes_cache.items()
        )
        stats += f"\nКружки: {len(self.circles_cache)}"
        await event.edit(f"📊 Статистика:\n{stats}")

    async def update_cache_cmd(self, event):
        """Обновление кеша"""
        await event.edit("🔄 Обновляю кеш...")
        await self.cache_messages()
        await event.edit("✅ Кеш обновлен!")

def setup(bot):
    MemesModule(bot)