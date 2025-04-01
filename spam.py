version = (1)

# this file was created for Hikka Usbot
# 🌐 https://github.com/stepka5/r3qui3mv_0id

# meta developer: @r3qui3mv_0ib
# scope: hikka_only
# scope: hikka_min 1.6.3

import asyncio
from asyncio import gather, sleep
from telethon.events import NewMessage

from .. import loader, utils

@loader.tds
class yg_spamMod(loader.Module):
    """спам модуль"""

    strings = {
        "name": "SPAM",
        "delay_set": "<b>задержка спама установлена на</b> <code>{}</code> <b>секунд</b> <emoji document_id=5420337710684467519>🤩</emoji>",
        "invalid_delay": "<b>неверное значение задержки. Укажите число больше 0.</b> <emoji document_id=5420337710684467519>🤩</emoji>",
        "delay_usage": "<b>укажите задержку в секундах.</b> <emoji document_id=5420337710684467519>🤩</emoji>",
    }
    spamming = False
    delay = 0.1  # Задержка по умолчанию

    async def spamcmd(self, message):
        """<число> <слово>"""
        if self.spamming:
            await utils.answer(
                message,
                "<b>уже запущен спам.</b> <i>используй</i> <code>.stopspam</code> <i>для остановки спама</i> <emoji document_id=5420388434248233181>🤩</emoji>",
            )
            await sleep(5)
            await message.delete()
            return

        args = utils.get_args(message)
        if len(args) < 2:
            await utils.answer(
                message,
                "<b>Используй:</b> <code>.spam <число> <текст></code> <emoji document_id=5420388434248233181>🤩</emoji>",
            )
            await sleep(5)
            await message.delete()
            return

        try:
            count = int(args[0])
            if count <= 0:
                await utils.answer(
                    message,
                    "<b>число должно быть больше нуля</b> <emoji document_id=5420388434248233181>🤩</emoji>",
                )
                await sleep(5)
                await message.delete()
                return
            word = " ".join(args[1:])
        except ValueError:
            await utils.answer(
                message,
                "<b>первый аргумент должен быть числом</b> <emoji document_id=5420388434248233181>🤩</emoji>",
            )
            await sleep(5)
            await message.delete()
            return

        self.spamming = True

        async def spam_task(num_messages):
            for _ in range(num_messages):
                if not self.spamming:
                    break  # Останавливаем спам, если флаг изменился
                await message.client.send_message(message.to_id, word)
                await asyncio.sleep(self.delay)  # Используем установленную задержку

        await utils.answer(
            message,
            f"<b>спам запущен</b> <code>{word}</code> <b>{count} раз.</b> <i>Используй</i> <code>.stopspam</code> <i>для остановки</i> <emoji document_id=5420388434248233181>🤩</emoji>",
        )
        await gather(*[spam_task(count)])
        self.spamming = False  # Убеждаемся, что spamming установлен в False после завершения задачи
        await sleep(10)
        await message.delete()
        return

    async def stopspamcmd(self, message):
        """остановить спам"""
        if not self.spamming:
            await utils.answer(
                message,
                "<b>спам не запущен</b> <emoji document_id=5420388434248233181>🤩</emoji>",
            )
            await sleep(5)
            await message.delete()
            return

        self.spamming = False
        await utils.answer(
            message,
            "<b>спам остановлен</b> <emoji document_id=5420388434248233181>🤩</emoji>",
        )
        await sleep(5)
        await message.delete()

    async def spamtimecmd(self, message):
        """<задержка>"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(
                message, self.strings["delay_usage"],
            )
            await sleep(5)
            await message.delete()
            return

        try:
            delay = float(args[0])
            if delay <= 0:
                await utils.answer(
                    message, self.strings["invalid_delay"],
                )
                await sleep(5)
                await message.delete()
                return

            self.delay = delay
            await utils.answer(
                message, self.strings["delay_set"].format(delay),
            )
            await sleep(5)
            await message.delete()

        except ValueError:
            await utils.answer(
                message, self.strings["invalid_delay"],
            )
            await sleep(5)
            await message.delete()

    async def client_ready(self, client, db):
        self.client = client