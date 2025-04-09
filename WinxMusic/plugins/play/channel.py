from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus, ChatType
from pyrogram.errors import ChatAdminRequired
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped, VideoPiped

from WinxMusic import app
from WinxMusic.utils.database import get_lang, set_cmode, get_cmode
from WinxMusic.utils.decorators.admins import admin_actual
from config import BANNED_USERS
from strings import command, get_command

# Inisialisasi PyTgCalls
pytgcalls = PyTgCalls(app)


# Perintah untuk mengatur Channel Play
@app.on_message(command("CHANNELPLAY_COMMAND") & filters.group & ~BANNED_USERS)
@admin_actual
async def playmode_(client, message: Message, _):
    try:
        lang_code = await get_lang(message.chat.id)
        CHANNELPLAY_COMMAND = get_command(lang_code)["CHANNELPLAY_COMMAND"]
    except Exception:
        CHANNELPLAY_COMMAND = get_command("pt")["CHANNELPLAY_COMMAND"]
    if len(message.command) < 2:
        return await message.reply_text(
            _["cplay_1"].format(message.chat.title, CHANNELPLAY_COMMAND[0])
        )
    query = message.text.split(None, 2)[1].lower().strip()
    if (str(query)).lower() == "disable":
        await set_cmode(message.chat.id, None)
        return await message.reply_text("Channel Play Disabled")
    elif str(query) == "linked":
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


# Perintah untuk memutar musik di channel
@app.on_message(filters.command("cplay") & filters.group & ~BANNED_USERS)
async def cplay(client, message: Message):
    chat_id = message.chat.id
    channel_id = await get_cmode(chat_id)
    if not channel_id:
        return await message.reply_text(
            "❌ Channel belum diatur. Gunakan perintah `/channelplay linked` atau `/channelplay @username_channel` untuk menghubungkan channel terlebih dahulu."
        )
    if len(message.command) < 2:
        return await message.reply_text("❌ Gunakan perintah: `/cplay <URL atau nama musik>`")

    query = message.text.split(None, 1)[1]
    try:
        await pytgcalls.join_group_call(
            channel_id,
            AudioPiped(query)
        )
        await message.reply_text(f"🎵 Sedang memutar musik di channel: {query}")
    except Exception as e:
        await message.reply_text(f"❌ Gagal memutar musik: {e}")


# Perintah untuk memutar video di channel
@app.on_message(filters.command("cvplay") & filters.group & ~BANNED_USERS)
async def cvplay(client, message: Message):
    chat_id = message.chat.id
    channel_id = await get_cmode(chat_id)
    if not channel_id:
        return await message.reply_text(
            "❌ Channel belum diatur. Gunakan perintah `/channelplay linked` atau `/channelplay @username_channel` untuk menghubungkan channel terlebih dahulu."
        )
    if len(message.command) < 2:
        return await message.reply_text("❌ Gunakan perintah: `/cvplay <URL atau nama video>`")

    query = message.text.split(None, 1)[1]
    try:
        await pytgcalls.join_group_call(
            channel_id,
            VideoPiped(query)
        )
        await message.reply_text(f"🎥 Sedang memutar video di channel: {query}")
    except Exception as e:
        await message.reply_text(f"❌ Gagal memutar video: {e}")


# Perintah untuk menghentikan musik atau video di channel
@app.on_message(filters.command("cend") & filters.group & ~BANNED_USERS)
async def cend(client, message: Message):
    chat_id = message.chat.id
    channel_id = await get_cmode(chat_id)
    if not channel_id:
        return await message.reply_text(
            "❌ Channel belum diatur. Gunakan perintah `/channelplay linked` atau `/channelplay @username_channel` untuk menghubungkan channel terlebih dahulu."
        )
    try:
        await pytgcalls.leave_group_call(channel_id)
        await message.reply_text("⏹️ Pemutaran musik atau video di channel telah dihentikan.")
    except Exception as e:
        await message.reply_text(f"❌ Gagal menghentikan pemutaran: {e}")