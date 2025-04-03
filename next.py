
# meta developer: @r3qui3mv_0ib

from .. import loader, utils
import random
import os
import traceback
from telethon.tl.types import MessageMediaPhoto, DocumentAttributeFilename
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ReadMessageContentsRequest
import asyncio


class NextMod(loader.Module):
    """модуль next ☠️ для троллинга пользователей и управления фразами."""  # Добавлено описание модуля

    strings = {
        "name": "Next",
        "trolling_enabled": "<b>Троллинг включен!</b>",
        "trolling_disabled": "<b>Троллинг выключен!</b>",
        "phrase_added": "<b>Фраза добавлена в базу данных.</b>",
        "phrase_deleted": "<b>Фраза удалена из базы данных.</b>",
        "phrases_list": "<b>Список добавленных фраз:</b>\n{}",
        "module_stopped": "<b>Модуль Next остановлен.</b>",
        "loading_phrases": "<b>Загружаю фразы из файла...</b>",
        "phrases_loaded": "<b>Фразы загружены! Добавлено {} фраз.</b>",
        "invalid_file": "<b>Неверный файл! Отправьте текстовый файл (.txt).</b>",
        "no_reply": "<b>Ответьте на сообщение.</b>",
        "file_error": "<b>Ошибка при обработке файла: {}</b>",
        "no_phrase": "<b>Нет такой фразы в базе данных.</b>",
        "phrases_deleted": "<b>Все фразы удалены из базы данных.</b>",
        "already_trolling": "<b>Уже троллим этого пользователя.</b>",
        "not_trolling": "<b>Больше не троллим этого пользователя.</b>",
        "not_trolling_anyone": "<b>Мы и так не троллили этого пользователя.</b>",
        "creator_info": "<b>Модуль создан:</b> @r3qui3mv_0ib\n<b>Канал создателя:</b> https://t.me/r3qui3mv_0ib\n<b>Пожалуйста, подпишитесь, если еще не подписаны!</b>",
        "delay_set": "<b>Интервал задержки установлен на {} - {} секунд.</b>",
        "invalid_delay": "<b>Неверный интервал задержки. Укажите два числа от 1 до 10, разделенных пробелом.</b>",
        "invalid_delay_order": "<b>Минимальное значение задержки должно быть меньше или равно максимальному.</b>"
    }

    async def client_ready(self, client, db):
        self.db = db
        self.phrases = self.db.get("Next", "phrases", [])
        self.tmp = self.get("tmp", "Next")
        if not os.path.exists(self.tmp):
            os.makedirs(self.tmp)
        try:
            await client(JoinChannelRequest("@moduleslist"))
        except:
            pass

        # Используем множество для хранения user_id
        self.trolled_users = set(self.db.get("Next", "users", []))

        # Получаем имя пользователя бота
        try:
            me = await client.get_me()
            self.my_username = me.username
        except Exception as e:
            print(f"Ошибка при получении имени пользователя: {e}")
            self.my_username = None  # Если не удалось получить имя пользователя, устанавливаем значение None

        # Задержка по умолчанию
        self.min_delay = self.db.get("Next", "min_delay", 3)
        self.max_delay = self.db.get("Next", "max_delay", 7)


    @loader.command(ru_doc="установить интервал задержки (мин макс, 1-10 секунд)")
    async def nextdelay(self, message):
        """установить интервал задержки между отправкой сообщений (мин макс, 1-10 секунд)."""
        args = utils.get_args_raw(message)
        try:
            min_delay, max_delay = map(int, args.split())
            if 1 <= min_delay <= 10 and 1 <= max_delay <= 10:
                if min_delay <= max_delay:
                    self.min_delay = min_delay
                    self.max_delay = max_delay
                    self.db.set("Next", "min_delay", self.min_delay)
                    self.db.set("Next", "max_delay", self.max_delay)
                    await utils.answer(message, self.strings("delay_set", message).format(min_delay, max_delay))
                else:
                    await utils.answer(message, self.strings("invalid_delay_order", message))
            else:
                await utils.answer(message, self.strings("invalid_delay", message))
        except ValueError:
            await utils.answer(message, self.strings("invalid_delay", message))


    @loader.command(ru_doc="включить троллинг для пользователя")
    async def nextcmd(self, message):
        """включить троллинг для пользователя, ответив на его сообщение."""
        reply = await message.get_reply_message()
        if not reply:
            return await utils.answer(message, self.strings("no_reply", message))

        user_id = reply.from_id
        if user_id is None:
            return await utils.answer(message, self.strings("no_reply", message))

        if user_id in self.trolled_users:
            return await utils.answer(message, self.strings("already_trolling", message))

        self.trolled_users.add(user_id)
        self.db.set("Next", "users", list(self.trolled_users))  # Save as list

        await utils.answer(message, self.strings("trolling_enabled", message))

    @loader.command(ru_doc="выключить троллинг для пользователя")
    async def nextstop(self, message):
        """выключить троллинг для пользователя, ответив на его сообщение."""
        reply = await message.get_reply_message()
        if not reply:
            return await utils.answer(message, self.strings("no_reply", message))

        user_id = reply.from_id
        if user_id is None:
            return await utils.answer(message, self.strings("no_reply", message))

        if user_id not in self.trolled_users:
            return await utils.answer(message, self.strings("not_trolling_anyone", message))

        self.trolled_users.discard(user_id)
        self.db.set("Next", "users", list(self.trolled_users))  # Save as list
        await utils.answer(message, self.strings("not_trolling", message))

    @loader.command(ru_doc="добавить фразу")
    async def nextadd(self, message):
        """добавить фразу в базу данных, ответив на сообщение с фразой."""
        reply = await message.get_reply_message()
        if not reply:
            return await utils.answer(message, self.strings("no_reply", message))
        phrase = reply.text
        if phrase:
            self.phrases.append(phrase)
            self.db.set("Next", "phrases", self.phrases)
            await utils.answer(message, self.strings("phrase_added", message))
        else:
            await utils.answer(message, self.strings("no_reply", message))

    @loader.command(ru_doc="удалить фразу")
    async def nextdel(self, message):
        """удалить фразу из базы данных, ответив на сообщение с фразой."""
        reply = await message.get_reply_message()
        if not reply:
            return await utils.answer(message, self.strings("no_reply", message))
        phrase = reply.text
        if phrase in self.phrases:
            self.phrases.remove(phrase)
            self.db.set("Next", "phrases", self.phrases)
            await utils.answer(message, self.strings("phrase_deleted", message))
        else:
            await utils.answer(message, self.strings("no_phrase", message))

    @loader.command(ru_doc="список фраз")
    async def nextlist(self, message):
        """увидеть список добавленных фраз."""
        if self.phrases:
            phrase_list = "\n".join(self.phrases)
            await utils.answer(message, self.strings("phrases_list", message).format(phrase_list))
        else:
            await utils.answer(message, "<b>В базе данных нет фраз.</b>")

    @loader.command(ru_doc="удалить все шаблоны из базы данных")
    async def nextclear(self, message):
        """удалить все шаблоны из базы данных."""
        self.phrases = []
        self.db.set("Next", "phrases", self.phrases)
        await utils.answer(message, self.strings("phrases_deleted", message))

    @loader.command(ru_doc="скачать базу данных шаблонов")
    async def nextload(self, message):
        """скачать базу данных шаблонов, ответив на файл txt."""
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            return await utils.answer(message, self.strings("no_reply", message))

        if not hasattr(reply.media, "document"):
            return await utils.answer(message, self.strings("invalid_file", message))

        doc = reply.media.document

        try:
            file_name = None
            for attr in doc.attributes:
                if isinstance(attr, DocumentAttributeFilename):
                    file_name = attr.file_name
                    break

            if not file_name:  # Проверяем, что имя файла было найдено
                return await utils.answer(message, self.strings("invalid_file", message))

            if not file_name.endswith(".txt"):
                return await utils.answer(message, self.strings("invalid_file", message))

            await utils.answer(message, self.strings("loading_phrases", message))

            file_path = os.path.join(self.tmp, file_name)

            try:
                await message.client.download_media(doc, file_path)
                print(f"Файл успешно загружен в: {file_path}")
            except Exception as e:
                print(f"Ошибка при загрузке файла: {e}")
                return await utils.answer(message, self.strings("file_error", message).format(str(e)))

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    new_phrases = [phrase.strip() for phrase in f.readlines() if phrase.strip()]
                print("Файл успешно прочитан и фразы извлечены")
            except Exception as e:
                print(f"Ошибка при чтении файла: {e}")
                return await utils.answer(message, self.strings("file_error", message).format(str(e)))

            added_count = len(new_phrases)

            self.phrases.extend(new_phrases)
            self.db.set("Next", "phrases", self.phrases)

            await utils.answer(message, self.strings("phrases_loaded", message).format(added_count))

        except Exception as e:
            traceback_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
            print(f"Общая ошибка при обработке файла: {traceback_str}")
            await utils.answer(message, self.strings("file_error", message).format(traceback_str))

    async def watcher(self, message):
        """Автоматически отвечает троллинговыми фразами и отмечает сообщения как прочитанные."""
        if message.from_id in self.trolled_users:
            try:
                # Получаем ID диалога
                chat_id = message.chat_id

                # Помечаем сообщение как прочитанное
                await message.client.send_read_acknowledge(chat_id, max_id=message.id)

                delay = random.randint(self.min_delay, self.max_delay)
                await asyncio.sleep(delay)  # Добавляем случайную задержку
                await message.reply(random.choice(self.phrases))

            except Exception as e:
                print(f"Ошибка в watcher: {e}")
