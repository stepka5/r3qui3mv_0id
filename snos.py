# meta developer: @r3qui3mv_0ib
from .. import loader, utils
from asyncio import sleep
import random
import logging

log = logging.getLogger(__name__)


@loader.tds
class SnosMod(loader.Module):
    """prank snos v1.0"""
    strings = {
        "name": "r3qui3mv_0id snos",
        "usage": "Загрузите модуль, чтобы использовать .snos.",
    }

    def __init__(self):
        pass

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    @loader.command(alias="snos")
    async def snos(self, message):
        """- делаем фек snos нахуй ."""

        #target = utils.get_args_raw(message)
        #if not target:
        #    await utils.answer(message, "⚠️ Укажите цель жалобы (никнейм, ID, ссылка).")
        #    return

        email_list = [
            "telegraph@telegram.net",
            "telegrafos@telegram.ru",
            "telegramm@telegraph.online",
            "telegram@telegraph.me",
            "telegrams@telegraph.io",
            "telegraphie@telegram.fr",
            "telegraphs@telegram.us",
            "telegram@telegraph.me",
            "telegramms@telegraph.pro",
            "telegraphia@telegram.tech",
            "abmin@telegram.org",
            "Yanekrofil@telegram.org",
            "Yasosbiby@telegram.org",
            "pornhab@rambler.com",
            "anal@telegram.org",
            "bongagans@gmail.ru",
            "snos@telegram.org",
            "porno@telegram.org",
            "dmca@telegram.org",
            "security@telegram.org",
            "stopCA@telegram.org",
            f"complaints{random.randint(10,99)}@telegram.org" # Новый адрес
        ]

        await utils.answer(message, "🔎 Поиск чатов...")
        await sleep(random.uniform(0.5, 1.0) * 0.7 * 0.75)

        await utils.answer(message, "🔍 Поиск сообщений...")
        await sleep(random.uniform(0.7, 1.2) * 0.7 * 0.75)

        await utils.answer(message, "🔬 Анализ сообщений...")
        await sleep(random.uniform(0.8, 1.3) * 0.7 * 0.75)

        await utils.answer(message, "⚠️ Поиск нарушений...")
        await sleep(random.uniform(0.9, 1.4) * 0.7 * 0.75)

        await utils.answer(message, "✅ Проверка жалоб...")
        await sleep(random.uniform(1.0, 1.5) * 0.7 * 0.75)

        await utils.answer(message, "🚀 Запуск сессий...")
        await sleep(random.uniform(1.1, 1.6) * 0.7 * 0.75)

        # Имитация рассылки на почты
        for i in range(30):
            email = random.choice(email_list)
            await utils.answer(message, f"📧 Рассылка жалобы на почту {i+1}: {email}...")
            await sleep(random.uniform(0.3, 0.7) * 0.7 * 0.75)

        await utils.answer(message, "✉️ Получение ответа...")
        await sleep(random.uniform(1.5, 2.0) * 0.7 * 0.75)

        await utils.answer(message, "📊 Анализ ответа...")
        await sleep(random.uniform(0.8, 1.3) * 0.7 * 0.75)

        response_messages = [
            "☠️ Ответ: Жалоба принята , тебе пизда ебаный лопух.",
            "☠️ Ответ: Благодарим , ему пизда щас снесем.",
            "☠️ Ответ: Нарушения найдены , хахаха лох.",
            "☠️ Ответ: Спасибо за обращение! ну мужик ты попал.",
            "☠️ Ответ: Жалоба передана , ЧУВАААААААААК.",
            "💰 Ответ: На пенек сел, $н0$ получил!.",
            "🤙 Ответ: ЧУВААААК, ТЕБІ ПІЗДА.",
            "🥟 ответ: Если через 5 минут по адресу: Улица Пушкина Дом колотушкина 42 не будет пачки пельменей за 198.99₽, прощайся с акком.",
            "😡 ответ: Ойй, шо творит молодой!",
            "🚔 ответ: ФСБ РФ уже у твоего дома, удачи!",
            "🚗 ответ: Картель едет к вам!.",
            "👍 ответ: Успешно отправил 1488 жалоб!",
        ]

        response = random.choice(response_messages)
        await utils.answer(message, "💬 Вывод ответа...")
        await sleep(random.uniform(0.3, 0.6) * 0.7 * 0.75)

        await utils.answer(message, response)