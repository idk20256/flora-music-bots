from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from WinxMusic import app
from WinxMusic.utils.database import is_on_off
from config import LOG, LOG_GROUP_ID

async def play_logs(message: Message, streamtype: str):
    if await is_on_off(LOG):
        # Menentukan username grup atau sebagai grup privat
        if message.chat.username:
            chatusername = f"@{message.chat.username}"
        else:
            chatusername = "🔒 Grup Pribadi"

        # Format pesan log
        logger_text = f"""
🎵 **Catatan Player - {app.mention}** 🎵

📌 **ID Obrolan:** `{message.chat.id}`
🏷️ **Nama Obrolan:** {message.chat.title}
🔗 **Username Grup:** {chatusername}

👤 **ID Pengguna:** `{message.from_user.id}`
📛 **Nama:** {message.from_user.mention}
📱 **Username:** @{message.from_user.username}

🔍 **Permintaan:** {message.text.split(None, 1)[1]}
🎧 **Jenis Aliran:** {streamtype}"""

        # Membuat tombol dengan nama pengguna
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="👤 Lihat Pengguna",
                        url=f"tg://user?id={message.from_user.id}",
                    )
                ]
            ]
        )

        # Mengirim log ke grup log jika bukan grup yang sama
        if message.chat.id != LOG_GROUP_ID:
            try:
                await app.send_message(
                    chat_id=LOG_GROUP_ID,
                    text=logger_text,
                    reply_markup=buttons,  # Menambahkan tombol
                    disable_web_page_preview=True,
                )
            except Exception as e:
                print(f"Error saat mengirim log: {e}")
        return