
# meta developer: @r3qui3mv_0ib
from .. import loader, utils
from asyncio import sleep
import random
import logging
from datetime import datetime

log = logging.getLogger(__name__)


@loader.tds
class DoxMod(loader.Module):
    """prank dox v1.0"""
    strings = {
        "name": "r3qui3mv_0id dox",
        "usage": "Загрузите модуль, чтобы использовать .doxlist.",
    }

    def __init__(self):
        pass

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.channel_username = "dox_hikka"
        self.channel_entity = None
        self.data = {}
        self.data_loaded = False

        await self.load_data_from_channel()

    async def load_data_from_channel(self):
        try:
            self.channel_entity = await self.client.get_entity(self.channel_username)
            messages = []
            async for message in self.client.iter_messages(self.channel_entity, limit=1000000):
                messages.append(message)

            previous_data = self.data.copy()
            self.data = {}
            added_counts = {}

            for message in messages:
                if message.message:
                    lines = message.message.splitlines()
                    if len(lines) > 1:
                        category = lines[0].strip()
                        data = [line.strip() for line in lines[1:] if line.strip()]

                        self.data[category] = data

                        added_counts[category] = 0
                        if category not in previous_data:
                            added_counts[category] = len(data)
                        else:
                            added_counts[category] = len(set(data) - set(previous_data[category]))

            self.data_loaded = True
            log.info(f"Данные из канала {self.channel_username} успешно загружены.")

            return added_counts

        except Exception as e:
            log.error(f"Ошибка при загрузке данных из канала: {e}")
            self.data = {}
            self.data_loaded = False
            return None

    def get_random_value(self, category):
        if category in self.data and self.data[category]:
            return random.choice(self.data[category])
        else:
            log.warning(f"Категория '{category}' не найдена или пуста.")
            return "Неизвестно"

    @loader.command(alias='dox')
    async def dox(self, message):
        """ - сделать фэйковый докс нахуй."""
        if not self.data_loaded:
            await utils.answer(message, "⚠️ <b>Данные еще не загружены. Пожалуйста, подождите немного.</b>")
            return

        if not self.data:
            await utils.answer(message, "⚠️ <b>Не удалось загрузить данные из канала. Проверьте логи.</b>")
            return

        await utils.answer(message, "👁️ <b>Запуск поиска...</b>")
        await sleep(0.5)

        search_phases = [
            ("🌐 Открытые источники", ["Сканирование соцсетей...", "Индексация сайтов...", "Поиск в базах данных..."]),
            ("🕵️‍♀️ Метаданные", ["Анализ профилей...", "Связи аккаунтов...", "Геолокация..."]),
            ("🔒 Утечки", ["Слитые базы...", "Пароли...", "Связанные аккаунты...", ""]),
            ("🤖 Анализ", ["Объединение данных...", "Закономерности...", "Генерация отчета..."])
        ]

        progress_symbols = ["|", "/", "-", "\\"]
        num_symbols = len(progress_symbols)

        for phase_name, sub_phases in search_phases:
            await utils.answer(message, f"👁️ <b>{phase_name}</b>")
            await sleep(0.2)

            for sub_phase in sub_phases:
                progress = 0
                symbol_index = 0
                start_time = datetime.now()
                animation_duration = 1.0

                while progress < 100:
                    elapsed_time = (datetime.now() - start_time).total_seconds()
                    if elapsed_time >= animation_duration:
                        progress = 100
                        break

                    progress = min(100, (elapsed_time / animation_duration) * 100)

                    current_symbol = progress_symbols[symbol_index % num_symbols]

                    await utils.answer(message,
                                        f"👁️ <b>{phase_name}</b> <i>[{int(progress)}%]</i>\n└ <i>{sub_phase}</i> {current_symbol}")

                    remaining_time = animation_duration - elapsed_time
                    sleep_duration = min(0.05, remaining_time / 20)
                    await sleep(sleep_duration)

                    symbol_index += 1

            await utils.answer(message, f"👁️ <b>{phase_name}</b> <i>[100%]</i>")
            await sleep(0.2)

        await utils.answer(message, "✅ <b>Поиск завершен!</b> 🤖")

        phone_number = self.get_random_value("phone_numbers")
        country = self.get_random_value("countries")
        region = self.get_random_value("regions")

        first_names_male = 'first_names_male'
        first_names_female = 'first_names_female'
        last_names_female = 'last_names_female'
        last_names_male = 'last_names_male'
        middle_names = 'middle_names'
        addresses = 'addresses'
        birth_dates = 'birth_dates'
        emails = 'emails'
        facebooks = 'facebooks'
        odnoklassniki = 'odnoklassniki'
        vkontakte = 'vkontakte'
        instagram = 'instagram'
        telegram_nicknames = 'telegram_nicknames'
        funny_facts = 'funny_facts'
        operators = 'operators'

        # Генерация нескольких возможных имен
        num_names = random.randint(2, 4)  # Случайное количество имен (от 2 до 4)
        possible_names = []
        for _ in range(num_names):
            gender = random.choice(['male', 'female'])
            if gender == 'male':
                possible_names.append(self.get_random_value(first_names_male))
            else:
                possible_names.append(self.get_random_value(first_names_female))

        # Генерация нескольких возможных ФИО
        num_full_names = random.randint(1, 3)  # Случайное количество ФИО (от 1 до 3)
        possible_full_names = []
        for _ in range(num_full_names):
            last_name = self.get_random_value(last_names_female)  # Или last_names_male, если нужно больше мужских ФИО
            first_name = self.get_random_value(first_names_female)  # Или first_names_male
            middle_name = self.get_random_value(middle_names)
            possible_full_names.append(f"{last_name} {first_name} {middle_name}")


        result_message = (
            f"📱\n"
            f"├ Номер: {phone_number}\n"
            f"├ Страна: {country}\n"
            f"├ Регион: {region}\n"
            f"├ Оператор: {self.get_random_value(operators)}\n\n"
            f"📓 Возможные имена:\n"
            f"└ {', '.join(possible_names)}\n\n"
            f"👤 Возможное ФИО: \n"
            f"  " + "\n  ".join(possible_full_names) + "\n\n"
            f"🏠 Адрес:\n"
            f"{self.get_random_value(addresses)}\n\n"
            f"🏥 Дата рождения: {', '.join([self.get_random_value(birth_dates) for _ in range(min(random.randint(1, 2), 2))])}\n"
            f"📪 Email: {', '.join([self.get_random_value(emails) for _ in range(min(random.randint(1, 2), 2))])}\n\n"
            f"👤 Facebook: {self.get_random_value(facebooks)}\n"
            f"👨‍🦳 Одноклассники: {self.get_random_value(odnoklassniki)}\n"
            f"🌐 ВКонтакте: {self.get_random_value(vkontakte)}\n"
            f"📷 Instagram: {self.get_random_value(instagram)}\n"
            f"📧 Telegram: {self.get_random_value(telegram_nicknames)}\n"
            f"🏪 Объявлений: {random.randint(0, 5)} шт\n\n"
            f"👁 Интересовались: {random.randint(1, 10000)} обезьян\n"
            f"🏅 Репутация: ({random.randint(0, 25)})👍 ({random.randint(0, 15)})👎 \n"
            f"😂 Забавный факт: {self.get_random_value(funny_facts)}\n"
            f"🔎 Расширенный поиск: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
        )
        await utils.answer(message, f"{result_message}")

    @loader.command(alias="doxlist")
    async def doxlist(self, message):
        """обновить базу данных"""
        await utils.answer(message, "🔄 <b>Обновление данных из канала...</b>")

        added_counts = await self.load_data_from_channel()

        if self.data_loaded and added_counts is not None:
            report = "✅ <b>База данных обновлена!</b>\n<b>Добавлено:</b>\n"
            for category, count in added_counts.items():
                report += f"├ {category}: {count}\n"
            await utils.answer(message, report)
        else:
            await utils.answer(message, "⚠️ <b>Не удалось обновить данные. Проверьте логи.</b>")
