import os
import io
import requests
from telethon import types, functions
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.account import UpdateProfileRequest, UpdateEmojiStatusRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.errors import UsernameNotOccupiedError, UsernameInvalidError

class CopyUserModule:
    def __init__(self, bot):
        self.bot = bot
        self.backup_data = None
        
        # Регистрация команд
        self.bot.register_command(
            cmd="copyuser",
            handler=self.copy_profile,
            description="Скопировать профиль пользователя (reply/@username/ID)"
        )
        self.bot.register_command(
            cmd="backupme",
            handler=self.backup_profile,
            description="Создать резервную копию вашего профиля"
        )
        self.bot.register_command(
            cmd="restoreme",
            handler=self.restore_profile,
            description="Восстановить профиль из резервной копии"
        )

    async def upload_to_0x0(self, photo_bytes):
        """Загрузка фото на временный хостинг"""
        try:
            files = {'file': ('photo.png', photo_bytes)}
            response = requests.post('https://0x0.st', files=files)
            return response.text.strip()
        except Exception:
            return None

    async def copy_profile(self, event):
        """Копирование профиля другого пользователя"""
        args = event.raw_text.split()[1:] if len(event.raw_text.split()) > 1 else []
        reply = await event.get_reply_message()
        
        try:
            # Определяем целевого пользователя
            if args:
                try:
                    user = await self.bot.client.get_entity(
                        int(args[0]) if args[0].isdigit() else args[0]
                    )
                except ValueError:
                    await event.edit("❌ Не удалось найти пользователя!")
                    return
            elif reply:
                user = await reply.get_sender()
            else:
                await event.edit("ℹ️ Укажите пользователя (reply/@username/ID)")
                return

            # Получаем полную информацию о пользователе
            full = await self.bot.client(GetFullUserRequest(user.id))
            user_info = full.users[0]
            me = await self.bot.client.get_me()
            
            # Копируем аватар
            if full.full_user.profile_photo:
                try:
                    photos = await self.bot.client.get_profile_photos(user.id)
                    if photos:
                        # Удаляем текущие фото профиля
                        await self.bot.client(DeletePhotosRequest(
                            await self.bot.client.get_profile_photos("me")
                        ))
                        
                        # Скачиваем и устанавливаем новое фото
                        photo = await self.bot.client.download_media(photos[0])
                        await self.bot.client(UploadProfilePhotoRequest(
                            file=await self.bot.client.upload_file(photo)
                        ))
                        os.remove(photo)
                except Exception as e:
                    print(f"Ошибка копирования аватара: {e}")

            # Обновляем профиль
            await self.bot.client(UpdateProfileRequest(
                first_name=user_info.first_name or "",
                last_name=user_info.last_name or "",
                about=full.full_user.about[:70] if full.full_user.about else "",
            ))

            # Копируем emoji-статус (если есть премиум)
            if hasattr(user_info, 'emoji_status') and user_info.emoji_status and me.premium:
                try:
                    await self.bot.client(
                        UpdateEmojiStatusRequest(
                            emoji_status=user_info.emoji_status
                        )
                    )
                except Exception:
                    pass
            
            await event.edit("✅ Профиль успешно скопирован!")

        except (UsernameNotOccupiedError, UsernameInvalidError):
            await event.edit("🚫 Пользователь не найден или неверный username!")
        except Exception as e:
            await event.edit(f"😵 Ошибка: {str(e)}")

    async def backup_profile(self, event):
        """Создание резервной копии профиля"""
        try:
            user = await self.bot.client.get_me()
            full = await self.bot.client(GetFullUserRequest(user.id))
            user_info = full.users[0]
            
            # Сохраняем аватар
            avatar_url = None
            photos = await self.bot.client.get_profile_photos(user.id)
            if photos:
                photo = await self.bot.client.download_media(photos[0], bytes)
                avatar_url = await self.upload_to_0x0(photo)

            # Сохраняем emoji-статус
            emoji_status_id = None
            if hasattr(user_info, 'emoji_status') and user_info.emoji_status:
                emoji_status_id = user_info.emoji_status.document_id

            # Формируем backup
            self.backup_data = {
                "first_name": user_info.first_name,
                "last_name": user_info.last_name,
                "about": full.full_user.about,
                "avatar_url": avatar_url,
                "emoji_status_id": emoji_status_id
            }
            
            await event.edit(
                f"✅ Резервная копия создана!\n\n"
                f"📸 Аватар: {'сохранен' if avatar_url else 'отсутствует'}\n"
                f"🎭 Emoji статус: {'сохранен' if emoji_status_id else 'отсутствует'}"
            )

        except Exception as e:
            await event.edit(f"😵 Ошибка: {str(e)}")

    async def restore_profile(self, event):
        """Восстановление профиля из резервной копии"""
        try:
            if not self.backup_data:
                await event.edit("❌ Нет сохраненной резервной копии!")
                return

            me = await self.bot.client.get_me()
            
            # Восстанавливаем аватар
            if self.backup_data.get("avatar_url"):
                try:
                    # Удаляем текущие фото
                    photos = await self.bot.client.get_profile_photos('me')
                    await self.bot.client(DeletePhotosRequest(photos))
                    
                    # Загружаем сохраненный аватар
                    response = requests.get(self.backup_data["avatar_url"])
                    avatar_bytes = io.BytesIO(response.content)
                    
                    await self.bot.client(UploadProfilePhotoRequest(
                        file=await self.bot.client.upload_file(avatar_bytes)
                    ))
                except Exception as e:
                    print(f"Ошибка восстановления аватара: {e}")

            # Восстанавливаем профиль
            await self.bot.client(UpdateProfileRequest(
                first_name=self.backup_data.get("first_name", ""),
                last_name=self.backup_data.get("last_name", ""),
                about=self.backup_data.get("about", "")
            ))

            # Восстанавливаем emoji-статус
            if self.backup_data.get("emoji_status_id") and me.premium:
                try:
                    await self.bot.client(
                        UpdateEmojiStatusRequest(
                            emoji_status=types.EmojiStatus(
                                document_id=self.backup_data["emoji_status_id"]
                            )
                        )
                    )
                except Exception:
                    pass

            await event.edit("✅ Профиль успешно восстановлен!")

        except Exception as e:
            await event.edit(f"😵 Ошибка: {str(e)}")

def setup(bot):
    CopyUserModule(bot)