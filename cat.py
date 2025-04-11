
# meta developer: @r3qui3mv_0ib

import asyncio
import logging
import random

from telethon import functions, types
from telethon.errors import ChannelInvalidError, ChatAdminRequiredError, ChatWriteForbiddenError

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class CatModule(loader.Module):
    """
    модуль для отправки пикчи с котиками.
    """

    strings = {
        "name": "Cat",
        "no_posts": "<b>котики закончились.</b>",
        "all_posts_used": "<b>котиков больше неть , все котики были отправлены.</b>",
        "forward_error": "<b>произошла ошибка при отправке котика: </b>",
        "get_message_error": "<b>не удалось найти котика. кыс кыс кыс.</b>",
        "channel_not_found": "<b>котик не найден. Пожалуйста, проверьте имя пользователя.</b>",
    }

    def __init__(self):
        self.channels = {
            'catm': 'dfffffffdf',
            'catw': 'mmm_wwgsW',
            'catv': 'mmm_wwwHmM'
        }
        self.dfffffffdf_used = set()
        self.mmm_wwgsW_used = set()
        self.mmm_wwwHmM_used = set()
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

        self.dfffffffdf_used = set(self.db.get("Cat", "dfffffffdf_used", []))
        self.mmm_wwgsW_used = set(self.db.get("Cat", "mmm_wwgsW_used", []))
        self.mmm_wwwHmM_used = set(self.db.get("Cat", "mmm_wwwHmM_used", []))

    def _save_used_posts(self, channel_username, used_posts):
        self.db.set("Cat", f"{channel_username}_used", list(used_posts))

    async def _get_random_post(self, channel_username):
        try:
            channel = await self.client.get_entity(channel_username)
        except (ChannelInvalidError, ValueError):
            logger.warning(f"Invalid channel username: {channel_username}")
            return None, self.strings("channel_not_found", channel_username=channel_username)
        except Exception as e:
            logger.exception(f"Error getting entity for {channel_username}: {e}")
            return None, self.strings("channel_not_found", channel_username=channel_username)

        if channel_username == 'dfffffffdf':
            used_posts = self.dfffffffdf_used
        elif channel_username == 'mmm_wwgsW':
            used_posts = self.mmm_wwgsW_used
        elif channel_username == 'mmm_wwwHmM':
            used_posts = self.mmm_wwwHmM_used
        else:
            logger.error(f"Unknown channel: {channel_username}")
            return None, "<b>Неизвестный канал</b>"

        try:
            history = await self.client(functions.messages.GetHistoryRequest(
                peer=channel,
                offset_id=0,
                offset_date=None,
                add_offset=0,
                limit=1,
                max_id=0,
                min_id=0,
                hash=0
            ))
            total_messages = history.count
        except ChatAdminRequiredError:
            logger.warning(f"Admin rights required to access history for {channel_username}")
            return None, "<b>вы не админ котиков.</b>"
        except ChatWriteForbiddenError:
             logger.warning(f"Write access forbidden for {channel_username}")
             return None, "<b>котик злой.</b>"
        except Exception as e:
            logger.exception(f"Error getting history for {channel_username}: {e}")
            return None, self.strings("get_message_error")

        if total_messages <= len(used_posts):
            logger.info(f"All posts used from {channel_username}")
            return None, self.strings("all_posts_used", channel_username=channel_username).format(channel_username)

        attempts = 0
        while attempts < 10:
            random_id = random.randint(1, total_messages)
            if random_id not in used_posts:
                try:
                    messages = await self.client.get_messages(channel, ids=random_id)
                    if messages:
                        return messages, None
                except Exception as e:
                    logger.exception(f"Error getting message {random_id} from \
                                      {channel_username}: {e}")
                    await asyncio.sleep(0.5)
            attempts += 1
        logger.warning(f"Failed to retrieve a random post from \
                         {channel_username} after multiple attempts.")
        return None, self.strings("get_message_error")

    async def _forward_post(self, message, channel_key):
        channel_username = self.channels[channel_key]
        message_obj, error = await self._get_random_post(channel_username)

        if error:
            await utils.answer(message, error)
            return

        if message_obj:
            try:
                await self.client.send_message(message.chat_id, message_obj)
                if channel_username == 'dfffffffdf':
                    self.dfffffffdf_used.add(message_obj.id)
                    self._save_used_posts(channel_username, self.dfffffffdf_used)
                elif channel_username == 'mmm_wwgsW':
                    self.mmm_wwgsW_used.add(message_obj.id)
                    self._save_used_posts(channel_username, self.mmm_wwgsW_used)
                elif channel_username == 'mmm_wwwHmM':
                    self.mmm_wwwHmM_used.add(message_obj.id)
                    self._save_used_posts(channel_username, self.mmm_wwwHmM_used)

            except Exception as e:
                logger.exception(f"Error sending message to chat: {e}")
                error_message = self.strings("forward_error").format(e)
                await utils.answer(message, error_message)
        else:
            await utils.answer(message, self.strings("get_message_error"))

        try:
            await message.delete()
        except Exception as e:
            logger.warning(f"Failed to delete command message: {e}")

    @loader.command(ru_doc="для любимого котика")
    async def catm(self, message):
        await self._forward_post(message, 'catm')

    @loader.command(ru_doc="для любимой кошечки")
    async def catw(self, message):
        await self._forward_post(message, 'catw')

    @loader.command(ru_doc="видео с кошарами")
    async def catv(self, message):
        await self._forward_post(message, 'catv')
