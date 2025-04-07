# meta developer: @r3qui3mv_0ib

import asyncio
import random
import json
import logging
#from .. import loader  
from hikka import loader 
from .. import utils
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.errors import MessageNotModifiedError

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


@loader.tds
class MemesMod(loader.Module):
    """Мемасы"""

    strings = {
        "name": "Мемы",
        "channel_error": "<b>Не могу получить информацию о канале:</b> <code>{}</code>",
        "no_posts": "<b>Нет постов в этом канале.</b>",
        "help_message": """
        <b>Модуль Мемы</b>
        .шутка - отправить случайный пост из канала @shutkimemes
        .жоскиймем - отправить случайный пост из канала @joskiimems
        .смешноймем - отправить случайный пост из канала @smeshnoymems
        .смехуятина - отправить случайный пост из канала @smehuatinka
        .анекдот - отправить случайный пост из канала @anekdotsmemes
        .кружок - отправить случайный кружок из канала @ponnnnnit
        .мемлист - статистика мемов
        .обновитькеш - обновить кеш мемов
        """,
        "memelist_message": "<b>Статистика мемов:</b>\nШутки: {jokes_count}\nЖесткие мемы: {hard_memes_count}\nСмешные мемы: {funny_memes_count}\nСмешная всячина: {funny_stuff_count}\nАнекдоты: {anecdotes_count}\nКружки: {circles_count}",
        "no_circles": "<b>Нет кружков в канале.</b>",
        "all_memes_shown": "<b>Все мемы из этого канала были показаны. Попробуйте позже.</b>",
        "processing_message": "<emoji document_id={loading_emoji}>⌛</emoji> <b>Отправка {request_type}...</b>",
        "cache_updated": "<b>Кэш обновлён!</b>\nДобавлено:\nШутки: {jokes_added}\nЖёсткие мемы: {hard_memes_added}\nСмешные мемы: {funny_memes_added}\nСмешная всячина: {funny_stuff_added}\nАнекдоты: {anecdotes_added}\nКружки: {circles_added}",
        "sending_circle": "<emoji document_id={loading_emoji}>⌛</emoji> <b>Отправка кружка...</b>",
        "memelist": "Статистика мемов",
        "update_cache": "Обновить кэш",
    }

    def __init__(self):
        self.name = self.strings["name"]
        self.config = {
            "emojis": [
                "5283184741904833341",  # 👌
                "5377686056915181180",  # 💗
                "5318853178282746002",  # 🖕
                "5317051744444751648",  # 🥴
                "5319214110154432904",  # 🤔
                "5285208874092091461",  # ☀️
                "5317051744444751648",  # 🥴
                "5285019156796692745",  # 😁
                "5283012801479073926",  # 🧏‍♀️
            ],
            "loading_emojis": [
                "5402355073458123173",  # ⌛️
                "5287734473775918473",  # 🔼
                "5406745015365943482",  # ⬇️
                "5386367538735104399",  # ⌛
            ],
            "data_file": "memes_data.json",
            "channel_mapping": {
                "шутка": "@shutkimemes",
                "жоскиймем": "@joskiimems",
                "смешноймем": "@smeshnoymems",
                "смехуятина": "@smehuatinka",
                "анекдот": "@anekdotsmemes",
                "кружок": "@ponnnnnit"
            },
        }
        self.channel_entities = {}  
        self.memes_cache = {}  
        self.circles_cache = []
        self.sent_post_ids = {}  
        self.sent_circle_ids = set()

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

        self.load_data()
        await self.get_all_channel_entities()  
        await self.cache_all_messages()  

    async def get_channel_entity(self, channel_username):
        """Получение entity канала по его username"""
        try:
            channel_info = await self.client(GetFullChannelRequest(channel_username))
            return channel_info.chats[0]
        except Exception as e:
            logger.error(f"Не удалось получить информацию о канале {channel_username}: {e}")
            return None

    async def get_all_channel_entities(self):
        """Получаем entities для всех каналов и сохраняем в self.channel_entities"""
        tasks = [self.get_channel_entity(channel_username) for channel_username in self.config["channel_mapping"].values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for key, channel_username in self.config["channel_mapping"].items():
            result = results[list(self.config["channel_mapping"].keys()).index(key)]
            if isinstance(result, Exception):
                logger.exception(f"Ошибка при получении entity для канала {channel_username}: {result}")
            elif result:
                self.channel_entities[key] = result
            else:
                logger.warning(f"Не удалось получить entity для канала {channel_username}. Пропуск.")

    def load_data(self):
        """Загрузка данных из файла"""
        try:
            with open(self.config["data_file"], "r") as f:
                data = json.load(f)
                self.sent_post_ids = data.get("sent_post_ids", {})
                self.sent_circle_ids = set(data.get("sent_circle_ids", []))
        except (FileNotFoundError, json.JSONDecodeError):
            self.sent_post_ids = {}
            self.sent_circle_ids = set()

    def save_data(self):
        """Сохранение данных в файл"""
        data = {
            "sent_post_ids": self.sent_post_ids,
            "sent_circle_ids": list(self.sent_circle_ids),
        }
        try:
            with open(self.config["data_file"], "w") as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных в JSON: {e}")

    async def cache_all_messages(self):
        """Кеширование всех сообщений из каналов"""
        tasks = []
        for key, entity in self.channel_entities.items():
            if key == "кружок":
                tasks.append(self.get_all_messages(entity, only_circles=True))
            else:
                tasks.append(self.get_all_messages(entity))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, key in enumerate(self.channel_entities.keys()):
            result = results[i]
            try:
                if isinstance(result, Exception):
                    raise result
                if key == "кружок":
                    self.circles_cache = result
                else:
                    self.memes_cache[key] = result
                logger.info(f"Успешно кешировали сообщения из канала {self.config['channel_mapping'].get(key, 'Unknown')}")
            except Exception as e:
                logger.exception(f"Ошибка при кешировании сообщений из канала {self.config['channel_mapping'].get(key, 'Unknown')}: {e}")

    async def get_all_messages(self, peer, only_circles=False):
        """Получение всех сообщений из указанного канала"""
        all_messages = []
        offset_id = 0
        try:
            while True:
                messages = await self.client(
                    GetHistoryRequest(
                        peer=peer,
                        offset_id=offset_id,
                        offset_date=None,
                        add_offset=0,
                        limit=100,
                        max_id=0,
                        min_id=0,
                        hash=0,
                    )
                )
                if not messages.messages:
                    break
                all_messages.extend(messages.messages)
                if len(messages.messages) < 100:
                    break
                offset_id = messages.messages[-1].id
        except Exception as e:
            logger.error(f"Ошибка при получении сообщений из канала {peer}: {e}")

        if only_circles:
            return [m for m in all_messages if hasattr(m, 'video_note') and m.video_note is not None]
        else:
            return all_messages

    async def get_random_post(self, category):
        """Получение случайного поста из канала указанной категории"""
        try:
            if category not in self.memes_cache or not self.memes_cache[category]:
                logger.warning(f"Кэш мемов для {category} пуст.")
                return None

            channel_posts = self.memes_cache[category]
            if category not in self.sent_post_ids:
                self.sent_post_ids[category] = []

            available_posts = [p for p in channel_posts if p.id not in self.sent_post_ids[category]]

            if not available_posts:
                logger.info(f"Все мемы из канала {category} были отправлены. Сбрасываем список.")
                self.sent_post_ids[category] = []
                available_posts = channel_posts 

                if not available_posts:
                    logger.warning(f"Канал {category} пустой.")
                    return None  

            post = random.choice(available_posts)
            self.sent_post_ids[category].append(post.id)  
            self.save_data()  
            return post
        except Exception as e:
            logger.exception(f"Ошибка при получении случайного поста из канала {category}: {e}")
            return None

    async def get_random_circle(self):
        """Получение случайного кружка"""
        try:
            if not self.circles_cache:
                logger.warning("Кэш кружков пуст.")
                return None

            filtered_circles = [
                c for c in self.circles_cache if c.id not in self.sent_circle_ids
            ]
            if not filtered_circles:
                logger.info("Все кружки были отправлены.  Сбрасываем список.")
                self.sent_circle_ids = set()
                filtered_circles = [
                    c for c in self.circles_cache if c.id not in self.sent_circle_ids
                ]
                if not filtered_circles:
                    logger.warning("Нет доступных кружков.")
                    return None

            circle = random.choice(filtered_circles)
            self.sent_circle_ids.add(circle.id)
            self.save_data()
            return circle
        except Exception as e:
            logger.exception(f"Ошибка при получении случайного кружка: {e}")
            return None

    async def send_random_post(self, message, category, request_type):
        """Отправка случайного поста из указанного канала"""
        try:
            channel_username = self.config["channel_mapping"].get(category)
            if not channel_username:
                await utils.answer(message, "Категория не найдена.")
                return

            loading_emoji = random.choice(self.config["loading_emojis"])
            try:
                await self.client.edit_message(
                    message.chat_id,
                    message.id,
                    self.strings["processing_message"].format(request_type=request_type, loading_emoji=loading_emoji)
                )
            except MessageNotModifiedError:
                pass  # Сообщение не было изменено (возможно, оно такое же, как и раньше)

            post = await self.get_random_post(category)
            if post:
                random_emoji = random.choice(self.config["emojis"])
                text = post.message or ""
                new_text = f"<emoji document_id={random_emoji}>{chr(0x200d)}</emoji> <b>{request_type}</b>\n\n{text}"

                await self.client.send_message(
                    message.chat_id,
                    new_text,
                    file=post.media if hasattr(post, "media") else None,
                    reply_to=message.reply_to_msg_id,
                )
                await message.delete()

            else:
                try:
                    await self.client.edit_message(
                        message.chat_id,
                        message.id,
                        self.strings["all_memes_shown"]
                    )
                except MessageNotModifiedError:
                    pass
        except Exception as e:
            logger.exception(f"Ошибка при отправке случайного поста из канала {category}: {e}")

    async def send_random_circle(self, message):
        """Отправка случайного кружка"""
        try:
            entity = self.channel_entities.get("кружок")
            if not entity:
                await utils.answer(message, "Не настроен канал с кружками.")
                return

            loading_emoji = random.choice(self.config["loading_emojis"])

            try:
                await self.client.edit_message(
                    message.chat_id,
                    message.id,
                    self.strings["sending_circle"].format(loading_emoji=loading_emoji)
                )
            except MessageNotModifiedError:
                pass  # Сообщение не было изменено (возможно, оно такое же, как и раньше)

            circle = await self.get_random_circle()
            if circle:
                await self.client.send_message(
                    message.chat_id,
                    file=circle.video_note,
                    reply_to=message.reply_to_msg_id,
                )
                await message.delete()

            else:
                await utils.answer(message, self.strings["no_circles"])

        except Exception as e:
            logger.exception(f"Ошибка при отправке случайного кружка: {e}")

    async def count_posts(self, category):
        """Подсчет постов в указанном канале"""
        if category not in self.memes_cache:
            return 0
        return len(self.memes_cache[category])

    async def count_circles(self):
        """Подсчет кружков"""
        return len(self.circles_cache)

    @loader.command(ru_doc="отправить случайную шутку из канала")
    async def шутка(self, message):
        """Отправить случайную шутку из канала"""
        await self.send_random_post(message, "шутка", "шутка")

    @loader.command(ru_doc="отправить случайный жесткий мем из канала")
    async def жоскиймем(self, message):
        """Отправить случайный жесткий мем из канала"""
        await self.send_random_post(message, "жоскиймем", "жесткий мем")

    @loader.command(ru_doc="отправить случайный смешной мем из канала")
    async def смешноймем(self, message):
        """Отправить случайный смешной мем из канала"""
        await self.send_random_post(message, "смешноймем", "смешной мем")

    @loader.command(ru_doc="отправить случайную смешную всячину из канала")
    async def смехуятина(self, message):
        """Отправить случайную смешную всячину из канала"""
        await self.send_random_post(message, "смехуятина", "смехуятина")

    @loader.command(ru_doc="отправить случайный анекдот из канала")
    async def анекдот(self, message):
        """Отправить случайный анекдот из канала"""
        await self.send_random_post(message, "анекдот", "анекдот")

    @loader.command(ru_doc="отправить случайный кружок из канала")
    async def кружок(self, message):
        """Отправить случайный кружок из канала"""
        await self.send_random_circle(message)

    @loader.command(ru_doc="статистика мемов")
    async def мемлист(self, message):
        """Статистика мемов"""
        try:
            jokes_count = await self.count_posts("шутка")
            hard_memes_count = await self.count_posts("жоскиймем")
            funny_memes_count = await self.count_posts("смешноймем")
            funny_stuff_count = await self.count_posts("смехуятина")
            anecdotes_count = await self.count_posts("анекдот")
            circles_count = await self.count_circles()

            await utils.answer(
                message,
                self.strings["memelist_message"].format(
                    jokes_count=jokes_count,
                    hard_memes_count=hard_memes_count,
                    funny_memes_count=funny_memes_count,
                    funny_stuff_count=funny_stuff_count,
                    anecdotes_count=anecdotes_count,
                    circles_count=circles_count,
                ),
            )
        except Exception as e:
            logger.exception(f"Ошибка при получении статистики мемов: {e}")
            await utils.answer(message, "<b>Произошла ошибка при получении статистики мемов.</b>")

    @loader.command(ru_doc="обновить кеш мемов")
    async def обновитькеш(self, message):
        """Обновить кеш мемов"""
        try:
            # Get current counts
            jokes_count = await self.count_posts("шутка")
            hard_memes_count = await self.count_posts("жоскиймем")
            funny_memes_count = await self.count_posts("смешноймем")
            funny_stuff_count = await self.count_posts("смехуятина")
            anecdotes_count = await self.count_posts("анекдот")
            circles_count = await self.count_circles()

            await self.cache_all_messages()

            # Get new counts
            new_jokes_count = await self.count_posts("шутка")
            new_hard_memes_count = await self.count_posts("жоскиймем")
            new_funny_memes_count = await self.count_posts("смешноймем")
            new_funny_stuff_count = await self.count_posts("смехуятина")
            new_anecdotes_count = await self.count_posts("анекдот")
            new_circles_count = await self.count_circles()

            # Calculate added counts
            jokes_added = new_jokes_count - jokes_count
            hard_memes_added = new_hard_memes_count - hard_memes_count
            funny_memes_added = new_funny_memes_count - funny_memes_count
            funny_stuff_added = new_funny_stuff_count - funny_stuff_count
            anecdotes_added = new_anecdotes_count - anecdotes_count
            circles_added = new_circles_count - circles_count

            try:
                await utils.answer(
                    message,
                    self.strings["cache_updated"].format(
                        jokes_added=jokes_added,
                        hard_memes_added=hard_memes_added,
                        funny_memes_added=funny_memes_added,
                        funny_stuff_added=funny_stuff_added,
                        anecdotes_added=anecdotes_added,
                        circles_added=circles_added,
                    ),
                )
            except MessageNotModifiedError:
                logger.info("Сообщение не изменено (статистика не изменилась).")

        except Exception as e:
            logger.exception(f"Ошибка при обновлении кеша: {e}")
            await utils.answer(message, "<b>Произошла ошибка при обновлении кеша.</b>")
