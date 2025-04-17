from pyrogram.types import Message

from WinxMusic import app
from WinxMusic.utils.database import is_on_off
from config import LOG, LOG_GROUP_ID


async def play_logs(message: Message, streamtype: str):
    if await is_on_off(LOG):
        if message.chat.username:
            chatusername = f"@{message.chat.username}"
        else:
            chatusername = "🔒 Grup Pribadi"

        logger_text = f"""
🎵 **Catatan Player - {app.mention}** 🎵

📌 **ID Obrolan:** `{message.chat.id}`
🏷️ **Nama Obrolan:** {message.chat.title}
🔗 **Username Grup:** {chatusername}

👤 **ID Pengguna:** `{message.from_user.id}`
📛 **Nama:** {message.from_user.mention}
📱 **username:** @{message.from_user.username}

🔍 **Permintaan:** {message.text.split(None, 1)[1]}
🎧 **Jenis Aliran:** {streamtype}"""

        if message.chat.id != LOG_GROUP_ID:
            try:
                await app.send_message(
                    chat_id=LOG_GROUP_ID,
                    text=logger_text,
                    disable_web_page_preview=True,
                )
            except Exception:
                pass
        return
