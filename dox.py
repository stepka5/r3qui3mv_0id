
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
        "usage": "Загрузите модуль, чтобы использовать .docs.",
    }

    def __init__(self):
        pass

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    @loader.command(alias='dox')
    async def dox(self, message):
        """ - сделать фэйковый докс нахуй."""

        await utils.answer(message, "👁️ <b>Запуск поиска...</b>")
        await sleep(random.uniform(0.4, 0.8) * 0.7 * 0.75)  # Сокращено на 30% и 25%

        # 2. Этапы "сбора" данных
        search_phases = [
            ("🌐 Открытые источники", ["Сканирование соцсетей...", "Индексация сайтов...", "Поиск в базах данных..."]),
            ("🕵️‍♀️ Метаданные", ["Анализ профилей...", "Связи аккаунтов...", "Геолокация..."]),
            ("🔒 Утечки", ["Слитые базы...", "Пароли...", "Связанные аккаунты..."]),
            ("🤖 Анализ", ["Объединение данных...", "Закономерности...", "Генерация отчета..."])
        ]

        total_phases = len(search_phases)
        current_phase = 0

        # Символы прогресса (как в Eye of God)
        progress_symbols = ["|", "/", "-", "\\"]  # Вертикальная черта и другие символы
        num_symbols = len(progress_symbols)

        for phase_name, sub_phases in search_phases:
            current_phase += 1
            await utils.answer(message, f"👁️ <b>{phase_name}</b>")
            await sleep(random.uniform(0.3, 0.5) * 0.7 * 0.75)  # Сокращено на 30% и 25%

            for sub_phase in sub_phases:
                # Красивая анимация прогресса
                progress = 0
                symbol_index = 0  # Инициализация индекса символа

                while progress < 100:
                    progress_increment = random.uniform(4, 8)  # Немного уменьшили прирост
                    progress = min(progress + progress_increment, 100)  # Обновление прогресса

                    # Получение текущего символа для анимации
                    current_symbol = progress_symbols[symbol_index % num_symbols]

                    await utils.answer(message,
                                        f"👁️ <b>{phase_name}</b> <i>[{int(progress)}%]</i>\n└ <i>{sub_phase}</i> {current_symbol}")
                    await sleep(0.1 * 0.7 * 0.75)  # Сокращено на 30% и 25%
                    symbol_index += 1  # Переход к следующему символу

            await utils.answer(message, f"👁️ <b>{phase_name}</b> <i>[100%]</i>")
            await sleep(random.uniform(0.2, 0.4) * 0.7 * 0.75)  # Сокращено на 30% и 25%

        await utils.answer(message, "✅ <b>Поиск завершен!</b> 🤖")
        await sleep(random.uniform(0.4, 0.7) * 0.7 * 0.75)  # Сокращено на 30% и 25%

        # 3. Расширенные данные:

        # Numbers:
        possible_numbers = [f"79{str(random.randint(100000000, 999999999))}" for _ in range(7)]  # Увеличили количество
        possible_numbers += [f"+7{str(random.randint(9000000000, 9999999999))}" for _ in range(5)]  # Увеличили количество
        possible_numbers += [f"8{str(random.randint(8000000000, 8999999999))}" for _ in range(3)]  # Увеличили количество
        possible_numbers += [f"{str(random.randint(10000000000, 69999999999))}" for _ in range(3)]  # Добавлены короткие номера

        # Добавил коды регионов с областями и больше вариантов
        russian_region_codes = {
            "Белгородская область": "472",
            "Брянская область": "483",
            "Владимирская область": "492",
            "Воронежская область": "473",
            "Ивановская область": "493",
            "Калужская область": "484",
            "Костромская область": "494",
            "Курская область": "471",
            "Липецкая область": "474",
            "Московская область": "495",
            "Орловская область": "486",
            "Рязанская область": "491",
            "Смоленская область": "481",
            "Тамбовская область": "475",
            "Тверская область": "482",
            "Тульская область": "487",
            "Ярославская область": "485",
            "Архангельская область": "818",
            "Астраханская область": "851",
            "Вологодская область": "817",
            "Калининградская область": "401",
            "Кировская область": "833",
            "Мурманская область": "815",
            "Новгородская область": "816",
            "Псковская область": "811",
            "Республика Карелия": "814",
            "Республика Коми": "821",
            "Республика Крым": "365",  # Новый регион
            "Севастополь": "869",  # Новый регион
            "Ростовская область": "863",  # Дополнительный регион
            "Краснодарский край": "861",  # Дополнительный регион
            "Республика Тыва": "394",  # Еще один регион
            "Забайкальский край": "302"  # И еще
        }

        # Выбираем случайный регион
        region = random.choice(list(russian_region_codes.keys()))
        region_code = russian_region_codes[region]

        # locations
        country = "Россия"

        # Names:

        first_names_male = ["еблан", "сосал?", "чмо", "андрей продац пылесос ", "санязабор", "вадим поросята", "антон велик", "анабель", "еблан", "петр первый", "александр шашлыки", "дима бздун", "серый гей", "ебаная чупакабра", "говно блохастое", "владимир красное солнышко", "алексей навальный ", "николай", "хуертём", "максим чо не спим", "егор ты зачем пукнул?", "кирилл - дебил", "ромашка", "дыня ебаная", "денчик и белка", "павлик наркоман", "антон гандон", "виктор баринов", "федя рыбак", "гриша хуй", "семя", "валера жопа", "олег грудастый ", "игорь серун", "стасик со стасиками", "русый пидор", "тимур поставщик", "эдуард тдд", "ярик гей", "мстислав часто мстит"]
        last_names_male = ["ченов", "пупкин", "говношкин", "я хочу какать", "пися", "поп", "ПИСЮЮЮЮН", "picun", "гнида тупая", "вы кто такие?", "перемоги не будет", "байден дай денег", "подмышкин", "анальный", "да это не я пенисы делаю", "воин дракона", "продажа бдсм игрушек", "песеньки с молочком", "козел", "орел бля", "го встр", "да я боюсь", "покажи жопу", "захаров попка орешек", "мне похуй я Филипп Киркоров", "дуров", "сережкин", "димин", "володька батя", "яков нахуй", "воробей меня не побей"]
        first_names_female = ["Дура", "Кисегач", "Кипяткова", "Шалава", "Проститутка", "Арбитражница", "Пельмень", "Шаурма горячая", "Крокодилдовна", "Галина парикмаХ3Р", "Конь Юлий", "Кунилингус", "Автобомобиииль", "Далбаебка", "Picun F6", "Цыганка ебаная", "Варвар", "Роплокс", "Рукоблудова", "Санчоус", "Александр электрик", "Не звонить суда", "Надежда пропала", "Гавно", "Мошонка", "Быков А Е", "Уебише", "Барбарис", "Свет пропал", "ZOV", "смертный вальс", "УЕбался об дверь"]
        last_names_female = ["молочко быка", "говно коровы", "курица", "карась", "хуй шрека", "говно", "конча", "обезьяна", "леди баг", "рак", "Лебедева", "Волкова", "тугая киска", "слив даши дошик", "жена ивана золо", "иван золо2004", "ах ох ах ах", "белая", "подруга с психушки", "оптимус", "мегатронова", "старскрим", "вылджек", "альфа трион", "ослина", "негр", "вильям бруно", "жена нагиева", "я хочу писать", "якубович", "picun"]
        middle_names = ["Дура", "Кисегач", "Кипяткова", "Шалава", "Проститутка", "Арбитражница", "Пельмень", "Шаурма горячая", "Крокодилдовна", "Галина парикмаХ3Р", "Конь Юлий", "Кунилингус", "Автобомобиииль", "Далбаебка", "Picun F6", "Цыганка ебаная", "Варвар", "Роплокс", "Рукоблудова", "Санчоус", "Александр электрик", "Не звонить суда", "Надежда пропала", "Гавно", "Мошонка", "Быков А Е", "Уебише", "Барбарис", "Свет пропал", "ZOV", "смертный вальс", "УЕбался об дверь"]

        # Школы, ВУЗы и другие учебные заведения
        education_places = ["МБОУ СОШ №1", "Лицей №2", "Гимназия №3", "СПбГУ", "МГУ", "Бауманка", "Шарага №69", "Хогвартс", "Школа для одаренных детей им. И.И. Петухова", "Курсы кройки и шитья", "ПТУ №13", "Академия ФСБ", "Военная академия РВСН", "Школа волшебства 'Дивногорье'", "Курсы повышения квалификации 'Рога и копыта'"]

        # More names and variations (убрали "10 Класс")
        names = [f"{random.choice(first_names_male)}", f"{random.choice(first_names_female)}", f"{random.choice(last_names_female)} {random.choice(first_names_female)}", f"{random.choice(last_names_male)}"]
        possible_full_names = [f"{random.choice(last_names_female)}",f"{random.choice(first_names_female)}",f"{random.choice(middle_names)}"]
        possible_full_names = [f"{random.choice(last_names_female)}",f"{random.choice(first_names_female)}",f"{random.choice(middle_names)}"]

        # Social (увеличили базу)
        facebooks = [f"{random.choice(last_names_female)} {random.choice(first_names_female)}", f"{random.choice(first_names_male)} {random.choice(last_names_male)}", f"profile.php?id={random.randint(1000000000, 9999999999)}", f"groups/{random.randint(1000000, 9999999)}", f"pages/{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(5, 15)))}", f"events/{random.randint(10000000, 99999999)}", "morgenstern_666", "durov", "spiderman.official", "batman.darkknight"] # Добавили
        odnoklassniki = [f"{random.choice(first_names_female)} {random.choice(last_names_female)}", f"{random.choice(first_names_female)}", f"{random.choice(first_names_female)} Прекрасная", f"id{random.randint(10000000, 99999999)}", f"profile/{random.randint(1000000, 9999999)}", f"group/{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(5, 15)))}"]
        vkontakte = [f"{random.choice(last_names_female)}.{random.choice(first_names_female)}", f"id{random.randint(10000000, 99999999)}", f"club{random.randint(1000000, 9999999)}", f"public{random.randint(1000000, 9999999)}", f"app{random.randint(1000000, 9999999)}", f"topic-{random.randint(100000, 999999)}_{random.randint(1, 100)}", "morgenstern666", "durov", "spider_man", "batman"]  # Добавлен вконтакте
        instagram = [f"@{ ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789_', k=random.randint(5, 15)))}", f"profile/{random.randint(1000000, 9999999)}", f"channel/{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(10, 20)))}", f"p/{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789_', k=random.randint(10, 15)))}", f"explore/tags/{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(5, 10)))}", "@morgen_shtern", "@durov", "@spiderman", "@batman"]  # Инстаграм
        telegram_nicknames = [f"@{ ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789_', k=random.randint(5, 15)))}", f"{random.choice(first_names_male + first_names_female)}{random.randint(100, 999)}", f"id{random.randint(10000000, 99999999)}", f"bot{random.randint(1000, 9999)}", f"channel{random.randint(1, 100)}", "@morgenshtern", "@durov", "@spider_official", "@the_batman"] # Добавил известных личностей


        # Дата рождения (еще увеличили)
        birth_dates = [f"{random.randint(1, 31)}.{random.randint(1, 12)}.{random.randint(1930, 2015)} ({datetime.now().year - random.randint(1930, 2015)} лет)" for _ in range(30)]
        emails = [f"yukozl0w4@yundex.ru", f"yukozl0w4@yandex.ru", f"juli.c0zlov4@yandex.ru", f"{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(5, 10)))}@gmail.com", f"{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(5, 10)))}@mail.ru", f"{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(5, 10)))}@yahoo.com", f"{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(5, 10)))}@outlook.com", f"{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(5, 10)))}@aol.com", f"spam{random.randint(100, 999)}@tempmail.com", f"info{random.randint(10, 99)}@example.org"]

        # Addresses (больше смешных)
        street_types = ["ул.", "пер.", "пр-кт", "ш.", "наб.", "аллея", "бул.", "проезд", "тупик"]
        city_names = ["Москва", "Санкт-Петербург", "Казань", "Новосибирск", "Екатеринбург", "Нижний Новгород", "Самара", "Омск", "Челябинск", "Ростов-на-Дону", "Уфа", "Красноярск", "Воронеж", "Пермь", "Волгоград", "Краснодар", "Саратов", "Тюмень", "Тольятти", "Ижевск", "Мухосранск", "Зажопинск", "Верхние Пупки", "Нижние Подмышки", "Дубай", "Майами", "Готэм", "Нью-Йорк"]  # Топ 20 городов России

        addresses = [f"{random.choice(city_names)}, {random.choice(street_types)} {random.choice(last_names_male + last_names_female)}, д.{random.randint(1, 200)}, кв.{random.randint(1, 500)}",
                     f"{random.choice(street_types)} {random.choice(last_names_male + last_names_female)}, {random.choice(city_names)}, д.{random.randint(1, 200)}",
                     f"г.{random.choice(city_names)}, {random.choice(street_types)} {random.randint(1, 100)}",
                     f"обл.{random.choice(list(russian_region_codes.keys()))}, г.{random.choice(city_names)}, {random.choice(street_types)} {random.choice(last_names_female)}",
                     f"Россия, {random.choice(city_names)}, д. {random.randint(1, 100)} (бомжатник)",
                     f"Планета Земля, г. {random.choice(city_names)}, д. {random.randint(1, 10)} (под лавкой)",
                     f"Марс, {random.choice(street_types)} {random.choice(last_names_male)}, д. {random.randint(1, 5)} (в кратере)",
                     f"Где-то в {random.choice(list(russian_region_codes.keys()))}, в лесу, на дереве, в дупле",
                     "Офис Telegram, Дубай",
                     "Бункер",
                     "Рублевка",
                     "в доме 673 по улице хуй соси",
                     "анал школьницы",
                     "собачья будка"
                     "остров гаитти",
                     "в рабстве у хасбика",
                     "Готэм, Бэт-пещера",
                     "Нью-Йорк, Квинс",] # Добавили

        # List of Operators
        operators = ["МТС", "Билайн", "Мегафон", "Tele2", "Yota", "Тинькофф Мобайл", "СберМобайл", "Ростелеком", "ВасяТелеком", "Хуефон"]
        operator = random.choice(operators)

        # Смешные факты (тоже увеличили)
        funny_facts = [
            "Любит котиков, но у него аллергия",
            "Считает себя экспертом по аниме",
            "Коллекционирует фантики от конфет",
            "Верит в рептилоидов",
            "Тайно пишет фанфики",
            "Боится голубей",
            "Разговаривает с комнатными растениями",
            "Засыпает под звуки пылесоса",
            "Мечтает полететь в космос на чайнике",
            "Считает, что Земля плоская",
            "Не умеет готовить яичницу",
            "В детстве мечтал стать космонавтом, но боится высоты",
            "Верит, что он избранный",
            "Умеет играть на воображаемой гитаре",
            "Спит в обнимку с плюшевым медведем",
            "Боится темноты, поэтому спит с ночником",
            "Считает, что он знает все языки мира, но говорит только на русском",
            "Называет свой компьютер 'Жорик'",
            "Думает, что он кот в человеческом обличии",
            "Питается только пельменями",
            "Иногда забывает дышать",
            "Умеет делать сальто назад, но только во сне",
            "Каждый день просыпается с мыслью о захвате мира",
            "Утверждает, что его лучший друг — инопланетянин",
            "Не отличает борщ от щей, но гордо называет себя гурманом.", # Юмор
            "Уверен, что знает все секреты вселенной, но не может найти второй носок.", # Юмор
            "Разговаривает со своим холодильником и просит его не шуметь ночью.", # Юмор
            "Считает, что у него есть суперспособность – всегда находить потерянные пульты от телевизора.", # Юмор
            "Мечтает стать космонавтом, чтобы сбежать от своих тараканов в голове.", # Юмор
            "Принимает ванну только в скафандре, чтобы не промокнуть.", # Юмор,
            "Считает себя реинкарнацией Наполеона, но боится лошадей.", # Юмор
            "Думает, что его кот - тайный агент спецслужб.", # Юмор
            "Верит, что Wi-Fi управляет его мыслями.", # Юмор
            "Утверждает, что знает будущее, но не может выиграть в лотерею.", # Юмор
            "Пытается майнить криптовалюту на калькуляторе.", # Юмор
            "Считает, что может общаться с дельфинами через ультразвук.", # Юмор,
            "Думает, что у него паучье чутье, но просто очень боится щекотки.",  # Юмор
            "Считает, что его бэтмобиль на самом деле - старенькая 'Ока'.",  # Юмор
            "Верит, что может летать, если достаточно сильно поверит в это (пока не пробовал).",  # Юмор
            "Уверен, что его суперсила - умение находить самые выгодные скидки в супермаркете.",  # Юмор
            "Считает, что его костюм супергероя стирает только мама в стиральной машинке.",  # Юмор
        ]

        # Увеличиваем базу юмора на 10%
        num_new_facts = int(len(funny_facts) * 0.1)
        new_funny_facts = [
            "Пытается научить своего кота разговаривать по-английски.",
            "Каждый раз при выходе из дома проверяет, выключил ли он утюг... пять раз.",
            "Иногда путает соль и сахар при готовке, и потом удивляется вкусу блюда.",
            "Верит, что если долго смотреть на кактус, то он заговорит.",
            "Считает, что умеет читать мысли, но пока ни разу не угадал." ,
            "Пересчитывает все ступеньки в подъезде каждый день.",
            "Боится, что однажды его разбудит восстание тостеров.",
            "Считает, что он Моргенштерн в душе, но мама против татуировок на лице.", # Юмор
            "Думает, что создал Telegram, но на самом деле просто активный пользователь.", # Юмор
            "Уверен, что Илон Маск - его дальний родственник.", # Юмор
            "Пытается баллотироваться в президенты каждый год, но забывает подать документы.", # Юмор,
            "Утверждает, что он Бэтмен, но летает только во сне.",  # Юмор
            "Считает, что его паутина сделана из супер-клея.",  # Юмор
            "Верит, что Леди Баг существует на самом деле и ждет его на крыше дома.",  # Юмор
            "Думает, что супермен на самом деле - журналист на пенсии.",  # Юмор
            "Уверен, что Гарри Поттер просто хорошо учился в школе.",  # Юмор
        ]
        funny_facts.extend(random.sample(new_funny_facts, min(num_new_facts, len(new_funny_facts))))



        # 4. Собираем сообщение:
        result_message = (
            f"📱\n"
            f"├ Номер: {random.choice(possible_numbers)}\n"
            f"├ Страна: {country}\n"
            f"├ Регион: {region}\n"
            f"├ Оператор: {operator}\n\n"
            f"📓 Возможные имена:\n"
            f"└ {', '.join(random.sample(names, min(random.randint(3, len(names)), 6)))}\n\n"
            f"👤 Возможное ФИО: \n"
            f"{'  '.join(random.sample(possible_full_names, min(random.randint(1, len(possible_full_names)), 4)))}\n\n"
            f"🏠 Адрес:\n"
            f"{random.choice(addresses)}\n\n"  # Адрес
            f"🏥 Дата рождения: {', '.join(random.sample(birth_dates, min(random.randint(3, len(birth_dates)), 6)))}\n"
            f"📪 Email: {', '.join(random.sample(emails, min(random.randint(1, len(emails)), 4)))}\n\n"
            f"👤 Facebook: {random.choice(facebooks)}\n"
            f"👨‍🦳 Одноклассники: {random.choice(odnoklassniki)}\n"
            f"🌐 ВКонтакте: {random.choice(vkontakte)}\n"  # Вк
            f"📷 Instagram: {random.choice(instagram)}\n"  # Инстаграм
            f"📧 Telegram: {random.choice(telegram_nicknames)}\n"
            f"🏪 Объявлений: {random.randint(0, 15)} шт\n\n"  # More realistic number
            f"👁 Интересовались: {random.randint(1, 20)} человек\n"  # More realistic number
            f"🏅 Репутация: ({random.randint(0, 50)})👍 ({random.randint(0, 30)})👎 \n"  # More realistic reputation
            f"😂 Забавный факт: {random.choice(funny_facts)}\n"  # Добавили забавный факт
            f"🔎 Расширенный поиск: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
        await utils.answer(message, f"{result_message}")

