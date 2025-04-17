from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from WinxMusic import app
from WinxMusic.utils.database import (
    delete_served_chat,
    get_assistant,
    is_on_off,
)
from config import LOG, LOG_GROUP_ID


@app.on_message(filters.new_chat_members)
async def on_bot_added(_, message: Message):
    try:
        if not await is_on_off(LOG):
            return
        userbot = await get_assistant(message.chat.id)
        chat = message.chat
        for members in message.new_chat_members:
            if members.id == app.id:
                count = await app.get_chat_members_count(chat.id)
                username = (
                    message.chat.username if message.chat.username else "ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ"
                )
                msg = (
                    f"🎉 **Bot musik ditambahkan ke grup baru #NewGroup**\n\n"
                    f"📋 **Nama Obrolan:** {message.chat.title}\n"
                    f"🆔 **ID Obrolan:** {message.chat.id}\n"
                    f"🔗 **Nama Pengguna Obrolan:** @{username}\n"
                    f"👥 **Jumlah Anggota Obrolan:** {count}\n"
                    f"👤 **Ditambahkan oleh:** {message.from_user.mention}"
                )
                await app.send_message(
                    LOG_GROUP_ID,
                    text=msg,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text=f"Ditambahkan oleh: {message.from_user.first_name}",
                                    user_id=message.from_user.id,
                                )
                            ]
                        ]
                    ),
                )
                if message.chat.username:
                    await userbot.join_chat(message.chat.username)
    except Exception:
        pass


@app.on_message(filters.left_chat_member)
async def on_bot_kicked(_, message: Message):
    try:
        if not await is_on_off(LOG):
            return
        userbot = await get_assistant(message.chat.id)

        left_chat_member = message.left_chat_member
        if left_chat_member and left_chat_member.id == app.id:
            remove_by = (
                message.from_user.mention
                if message.from_user
                else "Pengguna Tidak Dikenal"
            )
            title = message.chat.title
            username = (
                f"@{message.chat.username}" if message.chat.username else "Obrolan Pribadi"
            )
            chat_id = message.chat.id
            left = (
                f"🤖 O bot telah dihapus dari grup {title} #GroupRemoved\n"
                f"📋 **Nama Obrolan**: {title}\n"
                f"🆔 **ID Obrolan**: {chat_id}\n"
                f"🔗 **Nama Pengguna Obrolan**: {username}\n"
                f"👤 **Dihapus Oleh**: {remove_by}"
            )

            await app.send_message(
                LOG_GROUP_ID,
                text=left,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=f"Dihapus Oleh: {message.from_user.first_name}",
                                user_id=message.from_user.id,
                            )
                        ]
                    ]
                ),
            )
            await delete_served_chat(chat_id)
            await userbot.leave_chat(chat_id)
    except Exception as e:
        pass
