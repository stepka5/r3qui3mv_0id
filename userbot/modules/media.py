import os
from datetime import datetime
from telethon import events

class MediaModule:
    def __init__(self, bot):
        self.bot = bot
        self.media_dir = "downloads"
        os.makedirs(self.media_dir, exist_ok=True)
        self.setup_commands()
        
    def setup_commands(self):
        commands = [
            ("save", self.save_cmd, "Save media to downloads"),
            ("getlink", self.getlink_cmd, "Extract direct download links"),
        ]
        
        for cmd, handler, desc in commands:
            self.bot.register_command(cmd, handler, desc)
    
    async def save_cmd(self, event):
        if not event.reply_to_msg_id:
            await event.edit("⚠️ Reply to media message")
            return
            
        msg = await event.get_reply_message()
        if not msg.media:
            await event.edit("⚠️ No media found")
            return
            
        await event.edit("💾 Downloading...")
        path = await msg.download_media(f"{self.media_dir}/")
        await event.edit(f"✅ Saved to: <code>{path}</code>", parse_mode='HTML')

    async def getlink_cmd(self, event):
        # Implement link extraction logic
        await event.edit("🔗 This would extract direct download links")

def setup(bot):
    MediaModule(bot)