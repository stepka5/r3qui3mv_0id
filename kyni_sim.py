__version__ = (1, 0, 0)

# meta pic: https://img.icons8.com/emoji/48/tongue-emoji.png
# meta developer: @requiem_0in
# scope: hikka_only
# scope: hikka_min 1.0.0

from .. import loader
import asyncio
from datetime import datetime, timedelta
from telethon.tl.functions.messages import GetScheduledHistoryRequest
from telethon.tl.functions.messages import DeleteScheduledMessagesRequest

class KyniSimpleMod(loader.Module):
    """Модуль для отправки запланированных сообщений 'отлизать'"""
    
    strings = {"name": "KyniSimple"}
    
    def __init__(self):
        self.name = self.strings["name"]
        self._tasks = {}
    
    async def client_ready(self, client, db):
        self._client = client
        self._db = db
    
    async def kynicmd(self, message):
        """Отправлять сообщения 'отлизать': .kyni имя кол-во задержка [чат]"""
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if len(args) < 3:
            await message.edit("❌ Использование: .kyni [имя] [кол-во] [задержка] [чат]")
            return
            
        username = args[0]
        
        try:
            count = int(args[1])
        except ValueError:
            await message.edit("❌ Кол-во должно быть числом")
            return
            
        try:
            delay = float(args[2])
        except ValueError:
            await message.edit("❌ Задержка должна быть числом")
            return
        
        # Определение целевого чата
        target_chat = None
        if len(args) >= 4:
            target_chat_arg = args[3]
            try:
                # Проверяем, является ли аргумент числом (ID чата)
                if target_chat_arg.lstrip('-').isdigit():
                    target_chat_id = int(target_chat_arg)
                    try:
                        target_chat = await self._client.get_entity(target_chat_id)
                    except Exception:
                        # Если не удалось получить объект, используем просто ID
                        target_chat = target_chat_id
                else:
                    # Пробуем найти чат по имени/юзернейму
                    target_chat = await self._client.get_entity(target_chat_arg)
            except Exception as e:
                await message.edit(f"❌ Не могу найти чат {target_chat_arg}: {str(e)}")
                return
        else:
            # Если чат не указан, используем текущий
            target_chat = await message.get_chat()
        
        # Планируем сообщения через "Отправить позже"
        try:
            for i in range(count):
                schedule_time = datetime.now() + timedelta(hours=delay * (i + 1))
                schedule_timestamp = int(schedule_time.timestamp())
                
                try:
                    # Используем метод для отправки запланированного сообщения
                    await self._client.send_message(
                        entity=target_chat,
                        message=f"отлизать {username}",
                        schedule=schedule_timestamp
                    )
                except Exception as e:
                    await message.edit(f"❌ Ошибка при планировании сообщения: {str(e)}")
                    return
            
            # Определяем название чата для вывода
            if isinstance(target_chat, int):
                chat_name = f"чат с ID {target_chat}"
            else:
                chat_name = getattr(target_chat, 'title', None) or getattr(target_chat, 'username', None) or f"чат {getattr(target_chat, 'id', 'неизвестный')}"
            
            await message.edit(f"✅ Запланировано {count} сообщений 'отлизать {username}' в {chat_name} с интервалом {delay}ч")
        
        except Exception as e:
            await message.edit(f"❌ Ошибка: {str(e)}") 
