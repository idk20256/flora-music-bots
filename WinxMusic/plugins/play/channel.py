from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus, ChatType
from pyrogram.errors import ChatAdminRequired
from pyrogram.types import Message

from WinxMusic import app
from WinxMusic.utils.database import get_lang, set_cmode
from WinxMusic.utils.decorators.admins import admin_actual
from config import BANNED_USERS
from strings import command, get_command


@app.on_message(filters.group & ~BANNED_USERS)
@admin_actual
async def playmode_(client, message: Message, _):
    try:
        lang_code = await get_lang(message.chat.id)
        CHANNELPLAY_COMMAND = get_command(lang_code)["CHANNELPLAY_COMMAND"]
    except Exception:
        CHANNELPLAY_COMMAND = get_command("id")["CHANNELPLAY_COMMAND"]

    # Pisahkan logika untuk /play dan /cplay
    if message.text.startswith("/play"):
        # Logika untuk /play
        return await handle_group_play(client, message, _)
    elif message.text.startswith("/cplay"):
        # Logika untuk /cplay
        return await handle_channel_play(client, message, _, CHANNELPLAY_COMMAND)
    else:
        # Jika bukan perintah yang dikenali
        return await message.reply_text("Perintah tidak valid.")


async def handle_group_play(client, message: Message, _):
    # Tambahkan logika untuk pemutaran di grup
    return await message.reply_text("Memutar musik di grup.")


async def handle_channel_play(client, message: Message, _, CHANNELPLAY_COMMAND):
    # Periksa argumen perintah
    if len(message.command) < 2:
        return await message.reply_text(
            _["cplay_1"].format(message.chat.title, CHANNELPLAY_COMMAND[0])
        )
    query = message.text.split(None, 2)[1].lower().strip()
    if query == "disable":
        await set_cmode(message.chat.id, None)
        return await message.reply_text("Channel Play Dimatikan")
    elif query == "linked":
        chat = await app.get_chat(message.chat.id)
        if chat.linked_chat:
            chat_id = chat.linked_chat.id
            await set_cmode(message.chat.id, chat_id)
            return await message.reply_text(
                _["cplay_3"].format(chat.linked_chat.title, chat.linked_chat.id)
            )
        else:
            return await message.reply_text(_["cplay_2"])
    else:
        try:
            chat = await app.get_chat(query)
        except Exception:
            return await message.reply_text(_["cplay_4"])
        if chat.type != ChatType.CHANNEL:
            return await message.reply_text(_["cplay_5"])
        try:
            admins = app.get_chat_members(
                chat.id, filter=ChatMembersFilter.ADMINISTRATORS
            )
        except Exception:
            return await message.reply_text(_["cplay_4"])
        try:
            async for users in admins:
                if users.status == ChatMemberStatus.OWNER:
                    creatorusername = users.user.username
                    creatorid = users.user.id
        except ChatAdminRequired:
            return await message.reply_text(_["cplay_4"])

        if creatorid != message.from_user.id:
            return await message.reply_text(
                _["cplay_6"].format(chat.title, creatorusername)
            )
        await set_cmode(message.chat.id, chat.id)
        return await message.reply_text(_["cplay_3"].format(chat.title, chat.id))
