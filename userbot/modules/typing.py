import asyncio
from datetime import datetime, timedelta
from telethon import events
from telethon.tl.types import Message

class TypingAnimation:
    def __init__(self, bot):
        self.bot = bot
        self.typing_delay = 0.08
        self.typing_cursor = "▮"
        self.active_animations = {}
        
        # Регистрируем команды
        self.bot.register_command(
            cmd="p",
            handler=self.p_cmd,
            description="Анимация печати текста (.p текст)"
        )
        self.bot.register_command(
            cmd="п",
            handler=self.p_cyr_cmd,
            description="Анимация печати (альтернативная)"
        )
        self.bot.register_command(
            cmd="smena",
            handler=self.change_cursor,
            description="Изменить символ курсора (.smena ▯)"
        )
        self.bot.register_command(
            cmd="settimep",
            handler=self.set_delay,
            description="Изменить скорость печати (.settimep 0.1)"
        )
        self.bot.register_command(
            cmd="configp",
            handler=self.show_config,
            description="Показать текущие настройки"
        )

    async def animate_typing(self, event, text):
        chat_id = event.chat_id
        if chat_id in self.active_animations:
            return

        self.active_animations[chat_id] = True
        try:
            msg = await event.edit(self.typing_cursor)
            typed_text = ""
            
            for char in text:
                if chat_id not in self.active_animations:
                    break
                    
                typed_text += char
                await msg.edit(typed_text + self.typing_cursor)
                await asyncio.sleep(self.typing_delay)
            
            if chat_id in self.active_animations:
                await msg.edit(typed_text)
        finally:
            self.active_animations.pop(chat_id, None)

    async def p_cmd(self, event):
        text = event.raw_text[3:].strip()  # Убираем ".p "
        if not text:
            await event.edit("ℹ️ Используйте: <code>.p текст</code>")
            return
        await self.animate_typing(event, text)

    async def p_cyr_cmd(self, event):
        text = event.raw_text[3:].strip()  # Убираем ".п "
        if not text:
            await event.edit("ℹ️ Используйте: <code>.п текст</code>")
            return
        await self.animate_typing(event, text)

    async def change_cursor(self, event):
        new_cursor = event.raw_text[7:].strip()  # Убираем ".smena "
        if not new_cursor:
            await event.edit("ℹ️ Укажите новый символ курсора")
            return
            
        self.typing_cursor = new_cursor
        await event.edit(f"✅ Курсор изменен на: {self.typing_cursor}")

    async def set_delay(self, event):
        try:
            new_delay = event.raw_text[9:].strip()  # Убираем ".settimep "
            if not new_delay:
                await event.edit("ℹ️ Укажите новую задержку")
                return
                
            self.typing_delay = float(new_delay)
            await event.edit(f"✅ Задержка изменена на: {self.typing_delay} сек")
        except ValueError:
            await event.edit("⚠️ Задержка должна быть числом (например 0.1)")

    async def show_config(self, event):
        moscow_time = (datetime.utcnow() + timedelta(hours=3)).strftime("%H:%M:%S %d.%m.%Y")
        
        config_text = (
            "⚙️ <b>Текущие настройки:</b>\n"
            f"▸ Курсор: <code>{self.typing_cursor}</code>\n"
            f"▸ Задержка: <code>{self.typing_delay} сек</code>\n"
            f"▸ Время МСК: <code>{moscow_time}</code>\n\n"
            "<b>Доступные команды:</b>\n"
            "▸ <code>.p текст</code> - Анимация печати\n"
            "▸ <code>.п текст</code> - Альтернативная команда\n"
            "▸ <code>.smena символ</code> - Изменить курсор\n"
            "▸ <code>.settimep число</code> - Изменить задержку\n"
            "▸ <code>.configp</code> - Показать настройки\n\n"
            "<b>Разработчик: @PlaySkam</b>"
        )
        
        await event.edit(config_text)

def setup(bot):
    TypingAnimation(bot)