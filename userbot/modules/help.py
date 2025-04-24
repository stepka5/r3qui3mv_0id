class HelpModule:
    def __init__(self, bot):
        self.bot = bot
        # Проверяем, существует ли self.bot.commands и является ли словарем
        if not hasattr(self.bot, 'commands') or not isinstance(self.bot.commands, dict):
            self.bot.commands = {}  # Инициализируем, если не существует

        self.bot.register_command("help", self.help_cmd, "Показать список команд")

        # Добавляем информацию о модуле в словарь commands
        self.bot.commands["help"] = {"handler": self.help_cmd, "description": "Показать список команд", "module": "Help"}

        print(f"Команда help зарегистрирована: {self.bot.commands['help']}")  # Отладочный принт

    async def help_cmd(self, event):
        print("Функция help_cmd вызвана")  # Отладочный принт
        """Меню помощи (разделяем текст)"""

        help_text = "📚 **Commands**\n"  # Заголовок (вне блока цитирования)
        help_text += "> -----------------------------\n"
        for cmd, data in sorted(self.bot.commands.items()):
            help_text += f"> ✦` .{cmd}` - {data['description']}\n"  # Разделяем код и текст

        help_text += "> -----------------------------\n"
        help_text += "ℹ️ For more details, use .help command"

        await event.edit(help_text) # Убираем parse_mode
def setup(bot):
    HelpModule(bot)