
# meta developer: @r3qui3mv_0ib
# meta channel: @r3qui3mv_0ib_channel

from telethon.errors import ChatAdminRequiredError, BadRequestError, UserPrivacyRestrictedError, UserNotMutualContactError
from telethon.tl.functions.channels import EditAdminRequest, InviteToChannelRequest, JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import (
    ChannelParticipantAdmin,
    ChannelParticipantCreator,
    ChatAdminRights,
    PeerChannel,
    PeerUser,
    ChatBannedRights,
    Channel
)
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import EditChatAdminRequest
from telethon.tl.functions.channels import EditBannedRequest

from telethon import types, errors

import logging
from datetime import datetime, timedelta
from .. import loader, utils
import re

log = logging.getLogger(__name__)

@loader.tds
class ChatManagementMod(loader.Module):
    """Управление чатом."""
    strings = {
        "name": "Chat Management",  # имя модуля
        "kickall_success": "удалено {} участников.",
        "no_admin_rights": "ошибка: нет прав администратора.",
        "unknown_error": "неизвестная ошибка: {}",
        "not_supergroup": "<b>это не супергруппа!</b>",
        "not_group": "<b>это не группа!</b>",
        "kick_none": "<b>кто хочет принудительно покинуть чат?</b>",
        "promote_none": "<b>кто хочет опку?</b>",
        "demote_none": "<b>укажи с кого снять админку?</b>",
        "who": "<b>кого...?</b>",
        "not_admin": "<b>я не администратор...</b>",
        "kicked": "<code>{}</code> <b>был кикнул!</b>\n<b>ID:</b> <code>{}</code>",
        "promoted": "<code>{}</code> <b>получил права администратора!</b>\n<b>ID:</b> <code>{}</code>",
        "demoted": "<code>{}</code> <b>потерял права администратора!</b>\n<b>ID:</b> <code>{}</code>",
        "mute_none": "<b>укажите пользователя и время мута.</b>",
        "mute_success": "<b>пользователь {} замучен на {}.</b>",
        "unmute_success": "<b>пользователь {} размьючен.</b>",
        "invalid_time": "<b>неверный формат времени.</b>",
        "unmute_none": "<b>укажите пользователя, которого нужно размутить.</b>",
    }

    def __init__(self):
        self.name = self.strings["name"]
        self._me = None
        self._admin_cache = {}  # Кэш для хранения списка админов для каждого чата
        self._mute_cache = {}  # Кэш для хранения информации о мутах

    async def client_ready(self, client, db):
        """Вызывается при загрузке модуля."""
        self._me = await client.get_me()
        self.client = client  # Сохраняем клиент
        self.db = db  # Сохраняем доступ к базе данных

    async def _get_admin_list(self, message, chat, use_cache=True):
        """получает список администраторов чата/канала."""
        chat_id = chat.id
        if use_cache and chat_id in self._admin_cache:
            return self._admin_cache[chat_id]

        try:
            admin_list = []
            async for participant in self.client.iter_participants(chat):  # Используем self.client
                if isinstance(participant.participant,
                              (ChannelParticipantAdmin, ChannelParticipantCreator)):
                    admin_list.append(participant.id)

            self._admin_cache[chat_id] = admin_list  # Сохраняем в кэш
            return admin_list

        except Exception as e:
            log.exception(f"ошибка при получении списка админов: {e}")
            return []

    @loader.command(ru_doc="получает список ID администраторов чата.",
                    eng_doc="Gets the list of admin IDs in the chat.")
    async def getadmins(self, message):
        """Использование: .getadmins"""
        try:
            chat = await message.get_chat()
            admin_list = await self._get_admin_list(message, chat, use_cache=False)  # Не используем кэш
            if admin_list:
                await utils.answer(message, f"ID администраторов: {', '.join(map(str, admin_list))}")
            else:
                await utils.answer(message, "в этом чате нет администраторов или не удалось получить их список.")
        except Exception as e:
            log.exception(f"Ошибка в getadmins: {e}")
            await utils.answer(message, self.strings["unknown_error"].format(e))

    @loader.command(ru_doc="удаляет всех участников чата (кроме администраторов, себя и ботов).",
                    eng_doc="Kicks all members except admins, self and bots.")
    async def kickall(self, message):
        """использование: .kickall"""
        try:
            chat = await message.get_chat()
            admin_list = await self._get_admin_list(message, chat)  # получаем список админов
            kicked_count = 0

            async for user in self.client.iter_participants(chat):  # Используем self.client
                if user.id in admin_list or user.id == message.sender_id or user.bot:
                    continue

                try:
                    await self.client.kick_participant(chat, user.id)  # Используем self.client
                    kicked_count += 1
                except ChatAdminRequiredError:
                    await utils.answer(message, self.strings["no_admin_rights"])
                    return
                except Exception as e:
                    log.exception(f"ошибка при удалении {user.username or user.id}: {e}")

            await utils.answer(message, self.strings["kickall_success"].format(kicked_count))

        except Exception as e:
            log.exception(f"Ошибка в kickall: {e}")
            await utils.answer(message, self.strings["unknown_error"].format(e))

    @loader.command(ru_doc="добавляет пользователей в чат по ID или username.",
                    eng_doc="Adds users to chat by their ID or username.")
    async def addusers(self, message):
        """Использование: .addusers <user_id1> <username2> ..."""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, "укажите ID или usernames пользователей для добавления.")
            return

        added_count = 0
        chat = await message.get_chat()
        chat_id = message.chat_id  # Correct way to get chat ID.

        for arg in args:
            try:
                user = await self.client.get_entity(arg)
                user_id = user.id

                try:
                    # Determine if it's a channel or a group and use the appropriate method.
                    # Check if the chat is a channel
                    if isinstance(chat, types.Channel):
                        # Check if the user is a mutual contact
                        try:
                            await self.client(GetFullUserRequest(user_id))
                            is_mutual_contact = True
                        except errors.UserNotMutualContactError:
                            is_mutual_contact = False

                        if is_mutual_contact:
                            # Add user to the channel
                            await self.client(InviteToChannelRequest(channel=chat_id, users=[user_id]))
                            added_count += 1
                            log.info(f"добавлен {user.username or user.id} в {chat.title or chat.id}")
                        else:
                            await utils.answer(message, f"Не удалось добавить {user.username or user.id}: Необходимо, чтобы пользователь начал диалог с ботом.")
                            log.warning(f"Не удалось добавить {user.username or user.id}: Необходимо, чтобы пользователь начал диалог с ботом.")


                    else:  # it's a group
                        await self.client(JoinChannelRequest(channel=chat_id))
                        await self.client(ImportChatInviteRequest(chat_id))
                        added_count += 1 # if its a group we'll just assume we're in and added successfully

                    log.info(f"добавлен {user.username or user.id} в {chat.title or chat.id}")

                except errors.UserPrivacyRestrictedError:
                    log.warning(f"Не удалось добавить {arg}: Privacy restricted.")
                    await utils.answer(message, f"Не удалось добавить {arg}: Privacy restricted.")
                except errors.ChatAdminRequiredError:
                    log.warning(f"Не удалось добавить {arg}: Chat Admin Required.")
                    await utils.answer(message, f"Не удалось добавить {arg}: Chat Admin Required.")
                except errors.UserNotMutualContactError:
                    await utils.answer(message, f"Не удалось добавить {user.username or user.id}: Необходимо, чтобы пользователь начал диалог с ботом.")
                    log.warning(f"Не удалось добавить {user.username or user.id}: Необходимо, чтобы пользователь начал диалог с ботом.")
                except Exception as e:
                    log.warning(f"Не удалось добавить {arg}: {e}")
                    await utils.answer(message, f"Не удалось добавить {arg}: {e}")

            except Exception as e:
                log.warning(f"Не удалось найти пользователя {arg}: {e}")
                await utils.answer(message, f"Не удалось найти пользователя {arg}: {e}")


        await utils.answer(message, f"добавлено {added_count} пользователей.")

    @loader.group_admin_ban_users
    @loader.ratelimit
    async def kickcmd(self, message):
        """кикнуть из чата."""
        if isinstance(message.to_id, PeerUser):
            return await utils.answer(message, self.strings["not_group"])
        user = None
        if message.is_reply:
            user = await utils.get_user(await message.get_reply_message())
        else:
            args = utils.get_args(message)
            if not args:
                return await utils.answer(message, self.strings["kick_none"])
            try:
                user = await self.client.get_entity(args[0])
            except Exception:
                return await utils.answer(message, self.strings["who"])
        if not user:
            return await utils.answer(message, self.strings["who"])
        log.debug(user)
        if user.is_self:
            if not (await message.client.is_bot()
                    or await self.allmodules.check_security(message)):
                return
        try:
            await self.client.kick_participant(message.chat_id, user.id)
        except BadRequestError:
            await utils.answer(message, self.strings["not_admin"])
        except Exception as e:
             await utils.answer(message, self.strings["unknown_error"].format(e))
        else:
            await self.allmodules.log("kick", group=message.chat_id, affected_uids=[user.id])
            await utils.answer(message,
                               self.strings["kicked"].format(utils.escape_html(user.first_name), user.id))

    @loader.group_admin_add_admins
    @loader.ratelimit
    async def promotecmd(self, message):
        """дать админку."""
        user = None
        rank = ""
        if message.is_reply:
            user = await utils.get_user(await message.get_reply_message())
        else:
            args = utils.get_args(message)
            if not args:
                return await utils.answer(message, self.strings["promote_none"])
            try:
                user = await self.client.get_entity(args[0])
                if len(args) > 1:
                    rank = ' '.join(args[1:])
            except Exception:
                return await utils.answer(message, self.strings["who"])

        if not user:
            return await utils.answer(message, self.strings["who"])
        log.debug(user)
        try:
            if message.is_channel:
                await self.client(EditAdminRequest(message.chat_id, user.id,
                                                    ChatAdminRights(post_messages=None,
                                                                    add_admins=None,
                                                                    invite_users=None,
                                                                    change_info=None,
                                                                    ban_users=None,
                                                                    delete_messages=True,
                                                                    pin_messages=True,
                                                                    edit_messages=None), rank))
        except BadRequestError:
            await utils.answer(message, self.strings["not_admin"])
        except Exception as e:
             await utils.answer(message, self.strings["unknown_error"].format(e))
        else:
            await self.allmodules.log("promote", group=message.chat_id, affected_uids=[user.id])
            await utils.answer(message,
                               self.strings["promoted"].format(utils.escape_html(user.first_name), user.id))

    @loader.group_admin_add_admins
    async def demotecmd(self, message):
        """снять админку."""
        user = None
        if message.is_reply:
            user = await utils.get_user(await message.get_reply_message())
        else:
            args = utils.get_args(message)
            if not args:
                return await utils.answer(message, self.strings["demote_none"])
            try:
                user = await self.client.get_entity(args[0])
            except Exception:
                return await utils.answer(message, self.strings["who"])

        if not user:
            return await utils.answer(message, self.strings["who"])
        log.debug(user)
        try:
            if message.is_channel:
                await self.client(EditAdminRequest(message.chat_id, user.id,
                                                    ChatAdminRights(post_messages=None,
                                                                    add_admins=None,
                                                                    invite_users=None,
                                                                    change_info=None,
                                                                    ban_users=None,
                                                                    delete_messages=None,
                                                                    pin_messages=None,
                                                                    edit_messages=None), ""))
            else:
                await self.client(EditChatAdminRequest(message.chat_id, user.id, False))
        except BadRequestError:
            await utils.answer(message, self.strings["not_admin"])
        except Exception as e:
             await utils.answer(message, self.strings["unknown_error"].format(e))
        else:
            await self.allmodules.log("demote", group=message.chat_id, affected_uids=[user.id])
            await utils.answer(message,
                               self.strings["demoted"].format(utils.escape_html(user.first_name), user.id))

    @loader.group_admin_ban_users
    async def mutecmd(self, message):
        """замутить пользователя на указанное время. пример: .мут @username 1h30m."""
        if message.is_reply:
            reply = await message.get_reply_message()
            user = await utils.get_user(reply)
            args = utils.get_args(message)
            if not args:
                return await utils.answer(message, self.strings["mute_none"])

            time_str = args[0]
        else:
            args = utils.get_args(message)
            if len(args) < 2:
                return await utils.answer(message, self.strings["mute_none"])

            try:
                user = await self.client.get_entity(args[0])
                time_str = args[1]
            except Exception:
                return await utils.answer(message, self.strings["who"])

        try:
            mute_time_delta = self._parse_time(time_str)

            if not mute_time_delta:
                return await utils.answer(message, self.strings["invalid_time"])

            until_date = datetime.now() + mute_time_delta

            await self.client(EditBannedRequest(
                message.chat_id,
                user.id,
                ChatBannedRights(
                    until_date=until_date,
                    send_messages=True,
                    send_media=True,
                    send_stickers=True,
                    send_gifs=True,
                    send_inline=True,
                    embed_links=True
                )
            ))

            await utils.answer(message, self.strings["mute_success"].format(utils.escape_html(user.first_name),
                                                                            time_str))

        except Exception as e:
            log.exception(f"ошибка при муте пользователя: {e}")
            await utils.answer(message, self.strings["unknown_error"].format(e))

    @loader.group_admin_ban_users
    async def unmutecmd(self, message):
        """размутить пользователя."""
        if message.is_reply:
            user = await utils.get_user(await message.get_reply_message())
        else:
            args = utils.get_args(message)
            if not args:
                return await utils.answer(message, self.strings["unmute_none"])
            try:
                user = await self.client.get_entity(args[0])
            except Exception:
                return await utils.answer(message, self.strings["who"])

        try:
            await self.client(EditBannedRequest(
                message.chat_id,
                user.id,
                ChatBannedRights(
                    until_date=None,
                    view_messages=False
                )
            ))

            await utils.answer(message, self.strings["unmute_success"].format(utils.escape_html(user.first_name)))

        except Exception as e:
            log.exception(f"ошибка при размуте пользователя: {e}")
            await utils.answer(message, self.strings["unknown_error"].format(e))

    def _parse_time(self, time_string):
        """Парсит строку времени в timedelta."""
        time_dict = {
            "w": r"((?P<weeks>\d+)w)?",
            "d": r"((?P<days>\d+)d)?",
            "h": r"((?P<hours>\d+)h)?",
            "m": r"((?P<minutes>\d+)m)?",
            "s": r"((?P<seconds>\d+)s)?",
        }
        pattern = "".join(time_dict.values())
        match = re.match(pattern, time_string)
        if not match:
            return None

        time_kwargs = {k: int(v) for k, v in match.groupdict().items() if v is not None}
        return timedelta(**time_kwargs)
