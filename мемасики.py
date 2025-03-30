
# meta developer: @r3qui3mv_0ib

import asyncio
import random
from .. import loader, utils
from telethon.tl.functions.channels import JoinChannelRequest, GetFullChannelRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputPeerChannel, InputPeerUser
from telethon.errors import MessageNotModifiedError, UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest, InviteToChannelRequest
from telethon.tl.types import ChannelParticipantCreator, ChannelParticipantAdmin, ChannelParticipant
from telethon.utils import get_display_name
from telethon import types
from telethon.tl.functions.messages import EditMessageRequest


class MemesMod(loader.Module):
    """модуль memes с интернетами для пользователей."""

    strings = {
        "name": "Memes",
        "channel_error": "<b>не удалось получить информацию о канале.</b>",
        "no_posts": "<b>не удалось получить информацию о канале.</b>",
        "join_error": "<b>не удалось подписаться на канал.</b>",
        "not_subscribed": "<b>для использования этой команды необходимо подписаться на канал <a href='https://t.me/EbanutiyAlex'>@EbanutiyAlex</a></b>",
        "help_message": """
        <b>модуль Memes</b>
        .шутка - высылает рандомный пост с канала {channel_username} с #шутка
        .жоскиймем - высылает пост с #жоскиймем
        .смешноймем - высылает пост с #смешноймем
        .анекдот - высылает пост с #анекдот
        .кружок - высылает рандомный кружок с канала ponnnnnit
        .мемлист - выводит статистику по мемам
        .обновитькеш - анализирует канал и добавляет новые посты в кеш
        канал с мемами <a href='https://t.me/EbanutiyAlex'>@EbanutiyAlex</a> - подпишись пожалуйста (это сделает модуль лучше)
        """,
        "memelist_message": "<b>статистика по мемам на канале {channel_username}:</b>\nшуток: {jokes_count}\nжоских мемов: {hard_memes_count}\nсмешных мемов: {funny_memes_count}\nанекдотов: {anecdotes_count}\nкружков: {circles_count}",
        "no_circles": "<b>На канале нет кружков.</b>",
        "all_memes_shown": "<b>Все мемы с этим хэштегом были показаны. Попробуйте позже.</b>",
        "cache_updated": "<b>Кэш обновлен!</b>\nДобавлено:\nШуток: {jokes_added}\nЖоских мемов: {hard_memes_added}\nСмешных мемов: {funny_memes_added}\nАнекдотов: {anecdotes_added}\nКружков: {circles_added}",
    }

    def __init__(self):
        self.name = self.strings["name"]
        self.channel_username = "@EbanutiyAlex"
        self.channel_id = None
        self.entity = None
        self.help = self.strings["help_message"].format(
            channel_username=self.channel_username
        )
        self.hashtags = ["#шутка", "#жоскиймем", "#смешноймем", "#анекдот"]
        self.circle_channel_username = "@ponnnnnit"  # Канал с кружочками
        self.circle_channel_id = None
        self.circle_entity = None
        self.sent_post_ids = {}  # Dictionary to store sent post IDs for each hashtag
        self.sent_circle_ids = set()  # Для хранения ID отправленных кружков
        self.is_ready = False  # Флаг готовности модуля
        self.all_messages_cache = {}  # Кеш всех сообщений

    async def client_ready(self, client, db):
        self.client = client
        self.is_ready = False
        try:
            # Попытка получить полную информацию о канале мемов
            full_channel_info = await client(GetFullChannelRequest(channel=self.channel_username))
            self.entity = full_channel_info.chats[0]  # Первый элемент chats - это обычно канал
            self.channel_id = self.entity.id

        except Exception as e:
            print(f"Ошибка при получении информации о канале (GetFullChannelRequest): {e}")
            print(self.strings["channel_error"])
            return  # Важно: выходим из функции, если не удалось получить инфо

        # Автоматически подписываемся на канал от имени бота
        try:
            await client(JoinChannelRequest(self.channel_username))
        except Exception as e:
            print(f"Ошибка при попытке подписаться на канал: {e}")
            print(self.strings["join_error"])

        # Получаем информацию о канале с кружочками
        try:
            circle_channel_info = await client(GetFullChannelRequest(channel=self.circle_channel_username))
            self.circle_entity = circle_channel_info.chats[0]
            self.circle_channel_id = self.circle_entity.id
        except Exception as e:
            print(f"Ошибка при получении информации о канале с кружочками: {e}")
            self.circle_entity = None
            self.circle_channel_id = None

        self.help = self.strings["help_message"].format(
            channel_username=self.channel_username
        )

        # После получения информации о каналах, кешируем сообщения
        await self.cache_all_messages()

        self.is_ready = True

    async def cache_all_messages(self):
        """Кеширует все сообщения из каналов."""
        self.all_messages_cache[self.channel_id] = await self.get_all_messages(self.entity)
        if self.circle_entity:
            self.all_messages_cache[self.circle_channel_id] = await self.get_all_messages(self.circle_entity)

    async def get_all_messages(self, peer, hashtag=None, only_circles=False):
        """Получает все сообщения из указанного peer, фильтруя по hashtag или только кружкам."""
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
                        limit=100,  # Можно увеличить для скорости, но не слишком много
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
                print(f"Ошибка при получении сообщений: {e}")
                break

        if hashtag:
            return [m for m in all_messages if m.raw_text and hashtag in m.raw_text]
        elif only_circles:
            return [m for m in all_messages if hasattr(m, 'video_note') and m.video_note is not None]
        else:
            return all_messages

    async def get_random_post(self, hashtag):
        """получает случайный пост с заданным хэштегом."""
        try:
            if hashtag not in self.sent_post_ids:
                self.sent_post_ids[hashtag] = set()

            # Используем кешированные сообщения
            if self.channel_id not in self.all_messages_cache:
                print("Сообщения для канала не кешированы. Обновляю кеш...")
                await self.cache_all_messages()
                if self.channel_id not in self.all_messages_cache:
                    print("Не удалось закешировать сообщения для канала.")
                    return None

            messages = self.all_messages_cache[self.channel_id]
            filtered_messages = [
                m for m in messages if m.raw_text and hashtag in m.raw_text and m.id not in self.sent_post_ids[hashtag]
            ]

            if not filtered_messages:
                # Reset sent IDs if all messages have been shown
                self.sent_post_ids[hashtag] = set()
                filtered_messages = [
                    m for m in messages if m.raw_text and hashtag in m.raw_text and m.id not in self.sent_post_ids[hashtag]
                ]
                if not filtered_messages:
                    return None  # No messages with this hashtag at all

            post = random.choice(filtered_messages)
            self.sent_post_ids[hashtag].add(post.id)  # Add the post ID to the set for this hashtag
            return post

        except Exception as e:
            print(e)
            return None

    async def send_random_post(self, message, hashtag):
        """высылает случайный пост с заданным хэштегом и удаляет команду."""
        if not self.is_ready:
            await utils.answer(message, "Модуль еще не инициализирован. Попробуйте позже.")
            return

        try:
            # проверяем, подписан ли пользователь на канал
            try:
                user = await self.client.get_entity(message.sender_id)
                await self.client(
                    GetParticipantRequest(
                        channel=self.entity,
                        participant=user,  # используем InputPeerUser(message.sender_id)
                    )
                )
            except Exception as e:
                # пользователь не подписан
                await utils.answer(message, self.strings["not_subscribed"])
                return

            post = await self.get_random_post(hashtag)
            if post:
                # отправляем сообщение
                await self.client.send_message(
                    message.chat_id,
                    post.message if post.message else "",  # отправляем текст, если есть
                    file=post.media if hasattr(post, 'media') and post.media else None,
                )
                # удаляем сообщение команды
                await message.delete()

            else:
                await utils.answer(message, self.strings["all_memes_shown"])  # Changed message here
        except Exception as e:
            print(f"ошибка при отправке/удалении: {e}")

    async def count_posts(self, hashtag):
        """считает количество постов с заданным хэштегом."""
        # Используем кешированные сообщения
        if self.channel_id not in self.all_messages_cache:
            await self.cache_all_messages()
            if self.channel_id not in self.all_messages_cache:
                return 0

        messages = self.all_messages_cache[self.channel_id]
        return len([m for m in messages if m.raw_text and hashtag in m.raw_text])

    async def count_circles(self):
        """считает количество кружков на канале."""
        if not self.circle_entity:
            return 0

        # Используем кешированные сообщения
        if self.circle_channel_id not in self.all_messages_cache:
            await self.cache_all_messages()
            if self.circle_channel_id not in self.all_messages_cache:
                return 0

        messages = self.all_messages_cache[self.circle_channel_id]
        return len([m for m in messages if hasattr(m, 'video_note') and m.video_note is not None])

    @loader.command(ru_doc="выводит статистику по мемам")
    async def мемлист(self, message):
        """выводит статистику по мемам."""
        if not self.is_ready:
            await utils.answer(message, "Модуль еще не инициализирован. Попробуйте позже.")
            return

        jokes_count = await self.count_posts("#шутка")
        hard_memes_count = await self.count_posts("#жоскиймем")
        funny_memes_count = await self.count_posts("#смешноймем")
        anecdotes_count = await self.count_posts("#анекдот")
        circles_count = await self.count_circles()  # Считаем кружки

        await utils.answer(
            message,
            self.strings["memelist_message"].format(
                channel_username=self.channel_username,
                jokes_count=jokes_count,
                hard_memes_count=hard_memes_count,
                funny_memes_count=funny_memes_count,
                anecdotes_count=anecdotes_count,
                circles_count=circles_count,
            ),
        )

    @loader.command(ru_doc="высылает рандомную шутку с канала")
    async def шутка(self, message):
        """высылает рандомную шутку."""
        await self.send_random_post(message, "#шутка")

    @loader.command(ru_doc="высылает жоский мем с канала")
    async def жоскиймем(self, message):
        """высылает жоский мем."""
        await self.send_random_post(message, "#жоскиймем")

    @loader.command(ru_doc="высылает смешной мем с канала")
    async def смешноймем(self, message):
        """высылает смешной мем."""
        await self.send_random_post(message, "#смешноймем")

    @loader.command(ru_doc="высылает анекдот с канала")
    async def анекдот(self, message):
        """высылает анекдот."""
        await self.send_random_post(message, "#анекдот")

    @loader.command(ru_doc="высылает рандомный кружок с канала")
    async def кружок(self, message):
        """Высылает рандомный кружок с канала ponnnnnit."""
        if not self.is_ready:
            await utils.answer(message, "Модуль еще не инициализирован. Попробуйте позже.")
            return

        if not self.circle_entity:
            await utils.answer(message, "Не удалось получить информацию о канале с кружочками.")
            return

        try:
            # Используем кешированные сообщения
            if self.circle_channel_id not in self.all_messages_cache:
                print("Сообщения для канала с кружками не кешированы. Обновляю кеш...")
                await self.cache_all_messages()
                if self.circle_channel_id not in self.all_messages_cache:
                    print("Не удалось закешировать сообщения для канала с кружками.")
                    return

            all_circles = [m for m in self.all_messages_cache[self.circle_channel_id] if hasattr(m, 'video_note') and m.video_note is not None]
            filtered_circles = [circle for circle in all_circles if circle.id not in self.sent_circle_ids]

            if not filtered_circles:
                # Reset sent IDs if all circles have been shown
                self.sent_circle_ids = set()
                filtered_circles = [circle for circle in all_circles if circle.id not in self.sent_circle_ids]
                if not filtered_circles:
                    await utils.answer(message, self.strings["no_circles"])
                    return

            circle = random.choice(filtered_circles)
            self.sent_circle_ids.add(circle.id)

            await self.client.send_message(
                message.chat_id,
                file=circle.video_note,
                reply_to=message.reply_to_msg_id,
            )
            await message.delete()

        except Exception as e:
            print(f"Ошибка при отправке кружка: {e}")
            await utils.answer(message, f"Произошла ошибка при отправке кружка: {e}")

    @loader.command(ru_doc="Анализирует канал и добавляет новые посты в кеш")
    async def обновитькеш(self, message):
        """Анализирует канал и добавляет новые посты в кеш."""
        if not self.is_ready:
            await utils.answer(message, "Модуль еще не инициализирован. Попробуйте позже.")
            return

        try:
            # Получаем все сообщения из канала
            new_messages = await self.get_all_messages(self.entity)
            new_circle_messages = await self.get_all_messages(self.circle_entity, only_circles=True) if self.circle_entity else []

            # Инициализация счетчиков
            jokes_added = 0
            hard_memes_added = 0
            funny_memes_added = 0
            anecdotes_added = 0
            circles_added = 0

            # Если канал уже есть в кэше
            if self.channel_id in self.all_messages_cache:
                # Находим новые сообщения (которых нет в кэше)
                cached_ids = {m.id for m in self.all_messages_cache[self.channel_id]}
                new_messages_to_cache = [m for m in new_messages if m.id not in cached_ids]

                # Подсчитываем и добавляем новые сообщения в кэш
                for m in new_messages_to_cache:
                    if m.raw_text:
                        if "#шутка" in m.raw_text:
                            jokes_added += 1
                        if "#жоскиймем" in m.raw_text:
                            hard_memes_added += 1
                        if "#смешноймем" in m.raw_text:
                            funny_memes_added += 1
                        if "#анекдот" in m.raw_text:
                            anecdotes_added += 1
                self.all_messages_cache[self.channel_id].extend(new_messages_to_cache)
            else:
                # Если канала еще нет в кэше, добавляем все сообщения
                self.all_messages_cache[self.channel_id] = new_messages
                for m in new_messages:
                    if m.raw_text:
                        if "#шутка" in m.raw_text:
                            jokes_added += 1
                        if "#жоскиймем" in m.raw_text:
                            hard_memes_added += 1
                        if "#смешноймем" in m.raw_text:
                            funny_memes_added += 1
                        if "#анекдот" in m.raw_text:
                            anecdotes_added += 1

            # Для канала с кружочками
            if self.circle_entity:
                if self.circle_channel_id in self.all_messages_cache:
                    cached_circle_ids = {m.id for m in self.all_messages_cache[self.circle_channel_id]}
                    new_circle_messages_to_cache = [m for m in new_circle_messages if m.id not in cached_circle_ids]
                    circles_added = len(new_circle_messages_to_cache)
                    self.all_messages_cache[self.circle_channel_id].extend(new_circle_messages_to_cache)

                else:
                    self.all_messages_cache[self.circle_channel_id] = new_circle_messages
                    circles_added = len(new_circle_messages)

            await utils.answer(
                message,
                self.strings["cache_updated"].format(
                    jokes_added=jokes_added,
                    hard_memes_added=hard_memes_added,
                    funny_memes_added=funny_memes_added,
                    anecdotes_added=anecdotes_added,
                    circles_added=circles_added,
                ),
            )

        except Exception as e:
            print(f"Ошибка при обновлении кэша: {e}")
            await utils.answer(message, f"Произошла ошибка при обновлении кэша: {e}")
