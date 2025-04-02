# meta developer: @r3qui3mv_0ib

import io
import requests
from .. import loader, utils
from g4f.client import AsyncClient
from colorama import init

init()

meta = {
    "name": "Генерация Изображений",
    "version": "1.0",
    "description": "Генерирует изображения на основе текстовых запросов с использованием модели Flux.",
    "author": "@r3qui3mv_0ib",
    "commands": {
        ".genimage": "Генерирует изображение на основе заданного запроса с использованием модели Flux.",
        ".imageconfig": "Настройка параметров генерации изображений (размер)."
    }
}


class ImageGenerationMod(loader.Module):
    """Генерирует изображения с использованием модели Flux."""

    strings = {
        "name": "ГенерацияИзображений",
        "size_set": "Размер изображения установлен на: {}",
        "current_size": "Текущий размер изображения: {}"
    }

    def __init__(self):
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.g4f_client = AsyncClient()
        self.image_size = self.db.get(self.name, "image_size", "512x512")

    async def flux(self, prompt):
        """Генерирует изображение на основе заданного запроса с использованием модели Flux."""
        try:
            response = await self.g4f_client.images.generate(
                model="flux",
                prompt=prompt,
                response_format="url",
                size=self.image_size
            )
            return response.data[0].url
        except Exception as e:
            return f"Ошибка при генерации изображения: {e}"

    @loader.command(ru_doc="Генерирует изображение на основе заданного запроса с использованием модели Flux.")
    async def genimagecmd(self, message):
        """genimage <запрос>"""
        try:
            prompt = utils.get_args_raw(message)
            if not prompt:
                await utils.answer(message, "<b>Дайте мне какой-нибудь запрос!</b>")
                return

            await utils.answer(message, "Flux генерирует ваше изображение...")
            image_url = await self.flux(prompt)

            if "Error" in image_url:
                await utils.answer(message, image_url)
            else:
                try:
                    response = requests.get(image_url, stream=True)
                    response.raise_for_status()

                    file_bytes = io.BytesIO(response.content)
                    file_bytes.name = "generated_image.jpg"

                    await self.client.send_file(message.chat_id, file_bytes, caption=f"Сгенерированное изображение для: {prompt}")
                    await message.delete()
                except Exception as e:
                    await utils.answer(message, f"Ошибка при отправке изображения: {e}")

        except Exception as e:
            await utils.answer(message, f"Ошибка: {e}")

    @loader.command(ru_doc="Настройка размера изображения.")
    async def imageconfigcmd(self, message):
        """imageconfig <размер> (например, 256x256, 512x512)"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["current_size"].format(self.image_size))
            return

        self.image_size = args
        self.db.set(self.name, "image_size", self.image_size)
        await utils.answer(message, self.strings["size_set"].format(self.image_size))
