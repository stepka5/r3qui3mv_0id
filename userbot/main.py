import os
import sys
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from git import Repo
from git.exc import GitCommandError

# Настройка логов
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("userbot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Константы
REQUIRED_CHANNEL = "r3qui3mv_0ib"
REPO_URL = "https://github.com/stepka5/r3qui3mv_0id.git"

class UserBot:
    def __init__(self):
        # Проверка сессии
        if not os.path.exists("userbot_session.session"):
            logger.error("Session file not found! Run setup first.")
            sys.exit(1)
        
        # Загрузка конфига
        try:
            from config import API_ID, API_HASH
            self.client = TelegramClient(
                StringSession(open("userbot_session.session").read()),
                API_ID,
                API_HASH
            )
        except ImportError:
            logger.error("Config file not found! Run setup first.")
            sys.exit(1)
            
        self.commands = {}
        self.restarting = False
        self.is_running = True
        
    def register_command(self, cmd, handler, description=""):
        self.commands[cmd] = {"handler": handler, "description": description}
        logger.info(f"Command registered: {cmd}")

    async def check_subscription(self):
        try:
            entity = await self.client.get_entity(REQUIRED_CHANNEL)
            result = await self.client.get_permissions(entity, await self.client.get_me())
            if not result.is_admin and not result.is_member:
                await self.client.send_message(
                    'me',
                    f"⚠️ Для использования бота необходимо подписаться на канал @{REQUIRED_CHANNEL}\n\n"
                    f"После подписки перезапустите бота командой .restart"
                )
                return False
            return True
        except Exception as e:
            logger.error(f"Subscription check error: {e}")
            return True

    async def load_modules(self):
        modules = [
            'modules.typing',
            'modules.memes',
            'modules.utill',
            'modules.media',
            'modules.help',
            'modules.copyuser',
            'modules.system'
        ]
        
        for module in modules:
            try:
                imported = __import__(module, fromlist=['setup'])
                imported.setup(self)
                logger.info(f"Module {module} loaded")
            except Exception as e:
                logger.error(f"Error loading module {module}: {e}")

    async def check_updates(self):
        try:
            repo = Repo(os.path.dirname(os.path.abspath(__file__)))
            origin = repo.remotes.origin
            origin.fetch()
            commits_behind = sum(1 for _ in repo.iter_commits('HEAD..origin/main'))
            return commits_behind > 0, commits_behind
        except Exception as e:
            logger.error(f"Update check failed: {e}")
            return False, 0

    async def update_bot(self):
        try:
            repo = Repo(os.path.dirname(os.path.abspath(__file__)))
            repo.remotes.origin.pull()
            logger.info("Bot updated successfully")
            return True
        except Exception as e:
            logger.error(f"Update failed: {e}")
            return False

    async def start(self):
        await self.client.start()
        
        if not await self.check_subscription():
            logger.warning("User not subscribed to required channel")
            self.is_running = False
            return
        
        await self.load_modules()
        
        @self.client.on(events.NewMessage(pattern=r'\.(\w+)'))
        async def handler(event):
            cmd = event.pattern_match.group(1)
            if cmd in self.commands:
                try:
                    await self.commands[cmd]["handler"](event)
                except Exception as e:
                    logger.error(f"Command error: {cmd} - {e}")
                    await event.edit(f"⚠️ Ошибка: {str(e)}")

        me = await self.client.get_me()
        logger.info(f"Bot started as @{me.username}")
        
        update_available, commits = await self.check_updates()
        if update_available:
            await self.client.send_message(
                'me', 
                f"🔔 Доступно обновление ({commits} коммитов)\n"
                "Используйте .update для установки"
            )
        
        await self.client.run_until_disconnected()

    async def stop(self):
        self.is_running = False
        logger.info("Stopping bot...")
        await self.client.disconnect()
        
    async def restart(self):
        self.restarting = True
        await self.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == "__main__":
    bot = UserBot()
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        if not bot.restarting:
            asyncio.run(bot.stop())
