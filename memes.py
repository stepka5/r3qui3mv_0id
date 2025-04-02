
# meta developer: @r3qui3mv_0ib, based on @C0dwiz

import asyncio
import random
import json
from .. import loader, utils
from telethon.tl.functions.channels import JoinChannelRequest, GetFullChannelRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputPeerChannel
from telethon.errors import MessageNotModifiedError
from telethon import types

@loader.tds
class MemesMod(loader.Module):
    """Мемы с интернетов"""

    strings = {
        "name": "Мемы",
        "channel_error": "<b>Не могу получить информацию о канале.</b>",
        "no_posts": "<b>Нет постов с этим хэштегом.</b>",
        "join_error": "<b>Не могу присоединиться к каналу.</b>",
        "not_subscribed": "<b>Подпишитесь на @EbanutiyAlex, чтобы использовать эту команду</b>",
        "help_message": """
        <b>Модуль Мемы</b>
        .шутка - отправить случайный пост из канала @EbanutiyAlex с #шутка
        .жоскиймем - отправить случайный пост из канала @EbanutiyAlex с #жоскиймем
        .смешноймем - отправить случайный пост из канала @EbanutiyAlex с #смешноймем
        .смехуятина - отправить случайный пост из канала @EbanutiyAlex с #смехуятина
        .анекдот - отправить случайный пост из канала @EbanutiyAlex с #анекдот
        .кружок - отправить случайный кружок из канала @ponnnnnit
        .мемлист - статистика мемов
        .обновитькеш - обновить кеш мемов
        """,
        "memelist_message": "<b>Статистика мемов на канале @EbanutiyAlex:</b>\nШутки: {jokes_count}\nЖесткие мемы: {hard_memes_count}\nСмешные мемы: {funny_memes_count}\nСмешная всячина: {funny_stuff_count}\nАнекдоты: {anecdotes_count}\nКружки: {circles_count}",
        "no_circles": "<b>Нет кружков в канале.</b>",
        "all_memes_shown": "<b>Все мемы с этим хэштегом были показаны. Попробуйте позже.</b>",
        "processing_message": "<emoji document_id={loading_emoji}>⌛</emoji> <b>Отправка {request_type}...</b>",
        "cache_updated": "<b>Кэш обновлён!</b>\nДобавлено:\nШутки: {jokes_added}\nЖёсткие мемы: {hard_memes_added}\nСмешные мемы: {funny_memes_added}\nСмешная всячина: {funny_stuff_added}\nАнекдоты: {anecdotes_added}\nКружки: {circles_added}",
        "sending_circle": "<emoji document_id={loading_emoji}>⌛</emoji> <b>Отправка кружка...</b>",
        "memelist": "Статистика мемов",
        "update_cache": "Обновить кэш",
    }

    def __init__(self):
        self.name = self.strings["name"]
        self.memes_channel_username = "@EbanutiyAlex"
        self.memes_channel_id = None
        self.memes_entity = None
        self.circles_channel_username = "@ponnnnnit"
        self.circles_channel_id = None
        self.circles_entity = None
        self.help = self.strings["help_message"]
        self.sent_post_ids = {}
        self.sent_circle_ids = set()
        self.memes_cache = {}  # Кеш для мемов по хэштегам
        self.circles_cache = []
        self.emojis = [
            "5283184741904833341",  # 👌
            "5377686056915181180",  # 💗
            "5318853178282746002",  # 🖕
            "5317051744444751648",  # 🥴
            "5319214110154432904",  # 🤔
            "5285208874092091461",  # ☀️
            "5317051744444751648",  # 🥴
            "5285019156796692745",  # 😁
            "5283012801479073926",  # 🧏‍♀️
        ]
        self.loading_emojis = [
            "5402355073458123173",  # ⌛️
            "5287734473775918473",  # 🔼
            "5406745015365943482",  # ⬇️
            "5386367538735104399",  # ⌛
        ]
        self.special_emoji = "5316880323710034698" #🕺 emoji id
        self.data_file = "memes_data.json"  # Keep for sent_post_ids
        self.circles_data_file = "circles_data.json"  # New file for circles
        self.hashtags = ["#шутка", "#жоскиймем", "#смешноймем", "#анекдот", "#смехуятина"]  # Список хэштегов

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

        self.load_data()

        # Get memes channel info
        try:
            channel_info = await client(GetFullChannelRequest(self.memes_channel_username))
            self.memes_entity = channel_info.chats[0]
            self.memes_channel_id = self.memes_entity.id
        except Exception as e:
            print(f"Error getting memes channel info: {e}")
            print(self.strings["channel_error"])

        # Get circles channel info
        try:
            channel_info = await client(GetFullChannelRequest(self.circles_channel_username))
            self.circles_entity = channel_info.chats[0]
            self.circles_channel_id = self.circles_entity.id
        except Exception as e:
            print(f"Error getting circles channel info: {e}")
            self.circles_entity = None
            self.circles_channel_id = None

        # Join channels
        try:
            await client(JoinChannelRequest(self.memes_channel_username))
        except Exception as e:
            print(f"Error joining memes channel: {e}")
            print(self.strings["join_error"])
        if self.circles_entity:
            try:
                await client(JoinChannelRequest(self.circles_channel_username))
            except Exception as e:
                print(f"Error joining circles channel: {e}")

        # Cache messages
        await self.cache_all_messages()

    def load_data(self):
        """Загрузка данных из файла"""
        try:
            # Load data from JSON
            with open(self.data_file, "r") as f:
                data = json.load(f)
                self.sent_post_ids = {k: set(v) for k, v in data.get("sent_post_ids", {}).items()}
                self.sent_circle_ids = set(data.get("sent_circle_ids", [])) # Load circles as set
        except (FileNotFoundError, json.JSONDecodeError):
            self.sent_post_ids = {}
            self.sent_circle_ids = set()

    def save_data(self):
        """Сохранение данных в файл"""
        # Save data to JSON
        data = {
            "sent_post_ids": {k: list(v) for k, v in self.sent_post_ids.items()},
            "sent_circle_ids": list(self.sent_circle_ids),
        }
        try:
            with open(self.data_file, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving sent_post_ids to JSON: {e}")

    async def cache_all_messages(self):
        """Кеширование всех сообщений из каналов"""
        if self.memes_entity:
            self.memes_cache = {}  # Reset cache
            for hashtag in self.hashtags:
                self.memes_cache[hashtag] = await self.get_all_messages(self.memes_entity, hashtag=hashtag)
        if self.circles_entity:
            self.circles_cache = await self.get_all_messages(self.circles_entity, only_circles=True)

    async def get_all_messages(self, peer, hashtag=None, only_circles=False):
        """Получение всех сообщений из указанного канала"""
        all_messages = []
        offset_id = 0
        while True:
            try:
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
                print(f"Error getting messages: {e}")
                break

        if hashtag:
            return [m for m in all_messages if m.raw_text and hashtag in m.raw_text]
        elif only_circles:
            return [m for m in all_messages if hasattr(m, 'video_note') and m.video_note is not None]
        else:
            return all_messages

    async def get_random_post(self, hashtag):
        """Получение случайного поста с указанным хэштегом"""
        if hashtag not in self.memes_cache or not self.memes_cache[hashtag]:
            print(f"Кэш мемов для {hashtag} пуст, обновляем...")
            await self.cache_all_messages()
            if hashtag not in self.memes_cache or not self.memes_cache[hashtag]:
                return None

        filtered_messages = [
            m
            for m in self.memes_cache[hashtag]
            if m.id not in self.sent_post_ids.get(hashtag, set())
        ]
        if not filtered_messages:
            # Reset sent IDs if all messages have been shown
            self.sent_post_ids[hashtag] = set()
            filtered_messages = [
                m
                for m in self.memes_cache[hashtag]
                if m.id not in self.sent_post_ids.get(hashtag, set())
            ]
            if not filtered_messages:
                return None

        post = random.choice(filtered_messages)
        if hashtag not in self.sent_post_ids:
            self.sent_post_ids[hashtag] = set()
        self.sent_post_ids[hashtag].add(post.id)
        self.save_data()  # Save data after sending
        return post

    async def get_random_circle(self):
        """Получение случайного кружка"""
        if not self.circles_cache:
            print("Кэш кружков пуст, обновляем...")
            await self.cache_all_messages()
            if not self.circles_cache:
                return None

        filtered_circles = [
            c for c in self.circles_cache if c.id not in self.sent_circle_ids
        ]
        if not filtered_circles:
            # Reset sent IDs if all circles have been shown
            self.sent_circle_ids = set()
            filtered_circles = [
                c for c in self.circles_cache if c.id not in self.sent_circle_ids
            ]
            if not filtered_circles:
                return None

        circle = random.choice(filtered_circles)
        self.sent_circle_ids.add(circle.id)
        self.save_data()
        return circle

    async def send_random_post(self, message, hashtag, request_type):
        """Отправка случайного поста с указанным хэштегом"""
        try:
            # Check if the user is subscribed to the channel
            try:
                channel = await self.client.get_entity(self.memes_channel_username)
                if isinstance(channel, types.User):
                    await utils.answer(message, self.strings["not_subscribed"])
                    return
            except Exception:
                await utils.answer(message, self.strings["not_subscribed"])
                return

            # Choose a random loading emoji
            loading_emoji = random.choice(self.loading_emojis)

            # Send processing message (EDIT the original command message)
            try:
                await self.client.edit_message(
                    message.chat_id,
                    message.id,
                    self.strings["processing_message"].format(request_type=request_type, loading_emoji=loading_emoji)
                )
            except MessageNotModifiedError:
                pass  # Message wasn't modified (maybe it's the same as before)

            post = await self.get_random_post(hashtag)
            if post:
                # Choose a random emoji
                random_emoji = random.choice(self.emojis)

                # Format the text
                text = post.message or ""
                text = text.replace(hashtag, "").strip()

                if hashtag in ["#жоскиймем", "#смешноймем"]:
                    new_text = f"<emoji document_id={random_emoji}>{chr(0x200d)}</emoji> <b>{request_type}</b>\n\n{text}"
                elif hashtag == "#смехуятина":
                    new_text = f"<emoji document_id={random_emoji}>{chr(0x200d)}</emoji> <b>{request_type}</b>\n\n{text}"
                else: # joke or anecdote
                    new_text = f"<emoji document_id={random_emoji}></emoji> {text}"  # No special emoji for jokes and anecdotes

                # Send the message
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
            print(f"Error sending post: {e}")

    async def send_random_circle(self, message):
        """Отправка случайного кружка"""
        if not self.circles_entity:
            await utils.answer(message, "Не настроен канал с кружками.")
            return

        try:
            # Choose a random loading emoji
            loading_emoji = random.choice(self.loading_emojis)

             # Send processing message (EDIT the original command message)
            try:
                await self.client.edit_message(
                    message.chat_id,
                    message.id,
                    self.strings["sending_circle"].format(loading_emoji=loading_emoji)
                )
            except MessageNotModifiedError:
                pass  # Message wasn't modified (maybe it's the same as before)

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
            print(f"Error sending circle: {e}")

    async def count_posts(self, hashtag):
        """Подсчет постов с указанным хэштегом"""
        if hashtag not in self.memes_cache:
            return 0
        return len(self.memes_cache[hashtag])

    async def count_circles(self):
        """Подсчет кружков"""
        return len(self.circles_cache)

    @loader.command(ru_doc="отправить случайную шутку из канала")
    async def шутка(self, message):
        """Отправить случайную шутку из канала"""
        await self.send_random_post(message, "#шутка", "шутку")

    @loader.command(ru_doc="отправить случайный жесткий мем из канала")
    async def жоскиймем(self, message):
        """Отправить случайный жесткий мем из канала"""
        await self.send_random_post(message, "#жоскиймем", "жесткий мем")

    @loader.command(ru_doc="отправить случайный смешной мем из канала")
    async def смешноймем(self, message):
        """Отправить случайный смешной мем из канала"""
        await self.send_random_post(message, "#смешноймем", "смешной мем")

    @loader.command(ru_doc="отправить случайную смешную всячину из канала")
    async def смехуятина(self, message):
        """Отправить случайную смешную всячину из канала"""
        await self.send_random_post(message, "#смехуятина", "смехуятина")

    @loader.command(ru_doc="отправить случайный анекдот из канала")
    async def анекдот(self, message):
        """Отправить случайный анекдот из канала"""
        await self.send_random_post(message, "#анекдот", "анекдот")

    @loader.command(ru_doc="отправить случайный кружок из канала")
    async def кружок(self, message):
        """Отправить случайный кружок из канала"""
        await self.send_random_circle(message)

    @loader.command(ru_doc="статистика мемов")
    async def мемлист(self, message):
        """Статистика мемов"""
        jokes_count = await self.count_posts("#шутка")
        hard_memes_count = await self.count_posts("#жоскиймем")
        funny_memes_count = await self.count_posts("#смешноймем")
        funny_stuff_count = await self.count_posts("#смехуятина")
        anecdotes_count = await self.count_posts("#анекдот")
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

    @loader.command(ru_doc="обновить кеш мемов")
    async def обновитькеш(self, message):
        """Обновить кеш мемов"""
        if not self.memes_entity:
            await utils.answer(message, "Не настроен канал с мемами.")
            return

        # Get current counts
        jokes_count = await self.count_posts("#шутка")
        hard_memes_count = await self.count_posts("#жоскиймем")
        funny_memes_count = await self.count_posts("#смешноймем")
        funny_stuff_count = await self.count_posts("#смехуятина")
        anecdotes_count = await self.count_posts("#анекдот")
        circles_count = await self.count_circles()

        await self.cache_all_messages()

        # Get new counts
        new_jokes_count = await self.count_posts("#шутка")
        new_hard_memes_count = await self.count_posts("#жоскиймем")
        new_funny_memes_count = await self.count_posts("#смешноймем")
        new_funny_stuff_count = await self.count_posts("#смехуятина")
        new_anecdotes_count = await self.count_posts("#анекдот")
        new_circles_count = await self.count_circles()

        # Calculate added counts
        jokes_added = new_jokes_count - jokes_count
        hard_memes_added = new_hard_memes_count - hard_memes_count
        funny_memes_added = new_funny_memes_count - funny_memes_count
        funny_stuff_added = new_funny_stuff_count - funny_stuff_count
        anecdotes_added = new_anecdotes_count - anecdotes_count
        circles_added = new_circles_count - circles_count

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

    @loader.command(ru_doc="статистика мемов")
    async def мемлист(self, message):
        """Статистика мемов"""
        jokes_count = await self.count_posts("#шутка")
        hard_memes_count = await self.count_posts("#жоскиймем")
        funny_memes_count = await self.count_posts("#смешноймем")
        funny_stuff_count = await self.count_posts("#смехуятина")
        anecdotes_count = await self.count_posts("#анекдот")
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

    @loader.command(ru_doc="обновить кеш мемов")
    async def обновитькеш(self, message):
        """Обновить кеш мемов"""
        if not self.memes_entity:
            await utils.answer(message, "Не настроен канал с мемами.")
            return

        # Get current counts
        jokes_count = await self.count_posts("#шутка")
        hard_memes_count = await self.count_posts("#жоскиймем")
        funny_memes_count = await self.count_posts("#смешноймем")
        funny_stuff_count = await self.count_posts("#смехуятина")
        anecdotes_count = await self.count_posts("#анекдот")
        circles_count = await self.count_circles()

        await self.cache_all_messages()

        # Get new counts
        new_jokes_count = await self.count_posts("#шутка")
        new_hard_memes_count = await self.count_posts("#жоскиймем")
        new_funny_memes_count = await self.count_posts("#смешноймем")
        new_funny_stuff_count = await self.count_posts("#смехуятина")
        new_anecdotes_count = await self.count_posts("#анекдот")
        new_circles_count = await self.count_circles()

        # Calculate added counts
        jokes_added = new_jokes_count - jokes_count
        hard_memes_added = new_hard_memes_count - hard_memes_count
        funny_memes_added = new_funny_memes_count - funny_memes_count
        funny_stuff_added = new_funny_stuff_count - funny_stuff_count
        anecdotes_added = new_anecdotes_count - anecdotes_count
        circles_added = new_circles_count - circles_count

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
