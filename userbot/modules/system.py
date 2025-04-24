import os
import sys
import asyncio
from datetime import datetime
from telethon import events

class SystemModule:
    def __init__(self, bot):
        self.bot = bot
        self.setup_commands()
        
    def setup_commands(self):
        commands = [
            ("stop", self.stop_cmd, "Остановить бота"),
            ("restart", self.restart_cmd, "Перезапустить бота"),
            ("update", self.update_cmd, "Обновить бота с GitHub"),
            ("logs", self.logs_cmd, "Показать логи бота"),
            ("status", self.status_cmd, "Показать статус бота"),
        ]
        
        for cmd, handler, desc in commands:
            self.bot.register_command(cmd, handler, desc)
    
    async def stop_cmd(self, event):
        """Остановка бота"""
        await event.edit("🛑 Останавливаю бота...")
        await self.bot.stop()
        
    async def restart_cmd(self, event):
        """Перезапуск бота"""
        await event.edit("🔃 Перезапускаю бота...")
        await self.bot.restart()
        
    async def update_cmd(self, event):
        """Обновление бота"""
        await event.edit("🔄 Проверяю обновления...")
        update_available, commits = await self.bot.check_updates()
        
        if update_available:
            await event.edit(f"⏬ Загружаю {commits} новых обновлений...")
            if await self.bot.update_bot():
                await event.edit("✅ Бот успешно обновлен! Перезапускаю...")
                await self.bot.restart()
            else:
                await event.edit("⚠️ Ошибка при обновлении")
        else:
            await event.edit("ℹ️ Обновлений не найдено")
            
    async def logs_cmd(self, event):
        """Показать логи"""
        try:
            if not os.path.exists("userbot.log"):
                await event.edit("📜 Файл логов не найден")
                return
                
            with open("userbot.log", "r") as f:
                logs = f.read()[-4000:]  # Последние 4000 символов
                
            if len(logs) < 100:
                await event.edit("📜 Логов пока очень мало")
                return
                
            await event.edit(f"📜 Последние логи:\n```\n{logs}\n```")
        except Exception as e:
            await event.edit(f"⚠️ Ошибка: {str(e)}")
            
    async def status_cmd(self, event):
        """Статус бота"""
        try:
            from psutil import Process, virtual_memory
            process = Process(os.getpid())
            
            status_text = (
                "🤖 Статус бота:\n"
                f"▸ Запущен: {'Да' if self.bot.is_running else 'Нет'}\n"
                f"▸ Память: {process.memory_info().rss / 1024 / 1024:.2f} MB\n"
                f"▸ CPU: {process.cpu_percent()}%\n"
                f"▸ Время работы: {datetime.now() - process.create_time()}\n"
                f"▸ Подписан на канал: {'Да' if await self.bot.check_subscription() else 'Нет'}"
            )
            
            await event.edit(status_text)
        except ImportError:
            await event.edit("ℹ️ Для полной статистики установите psutil: pip install psutil")
        except Exception as e:
            await event.edit(f"⚠️ Ошибка: {str(e)}")

def setup(bot):
    SystemModule(bot)
