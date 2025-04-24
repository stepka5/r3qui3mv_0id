import time
from telethon import events

class UtilityModule:
    def __init__(self, bot):
        self.bot = bot
        self.setup_commands()
        
    def setup_commands(self):
        commands = [
            ("ping", self.ping_cmd, "Check bot responsiveness"),
            ("id", self.id_cmd, "Get chat/user ID"),
            ("purge", self.purge_cmd, "Delete multiple messages"),
        ]
        
        for cmd, handler, desc in commands:
            self.bot.register_command(cmd, handler, desc)
    
    async def ping_cmd(self, event):
        start = time.time()
        msg = await event.edit("🏓 Pong!")
        end = time.time()
        await msg.edit(f"🏓 Pong! {round((end-start)*1000)}ms")

    async def id_cmd(self, event):
        text = f"👤 User ID: <code>{event.sender_id}</code>\n"
        if event.is_private:
            text += f"💬 Chat ID: <code>{event.chat_id}</code>"
        else:
            text += f"💬 Chat ID: <code>{event.chat_id}</code>\n"
            text += f"📄 Message ID: <code>{event.message.id}</code>"
        await event.edit(text, parse_mode='HTML')

    async def purge_cmd(self, event):
        if not event.reply_to_msg_id:
            await event.edit("⚠️ Reply to a message to purge from")
            return
            
        await event.edit("🧹 Purging messages...")
        msg_ids = []
        async for msg in self.bot.client.iter_messages(
            event.chat_id,
            min_id=event.reply_to_msg_id-1,
            reverse=True
        ):
            msg_ids.append(msg.id)
            if len(msg_ids) == 100:
                await self.bot.client.delete_messages(event.chat_id, msg_ids)
                msg_ids = []
                
        if msg_ids:
            await self.bot.client.delete_messages(event.chat_id, msg_ids)
            
        await event.delete()

def setup(bot):
    UtilityModule(bot)