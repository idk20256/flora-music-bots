import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus, ChatType
from datetime import datetime
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import Message

from WinxMusic import app  # Menggunakan instance bot musik Anda
from WinxMusic.utils.database import get_lang, set_cmode
from WinxMusic.utils.decorators.admins import admin_actual
from config import BANNED_USERS
from strings import command, get_command

# Variabel untuk menyimpan data absen
absen_data = {}

# Perintah untuk memulai sesi absen
@app.on_message(filters.command("absen") & filters.group & ~BANNED_USERS)
@admin_actual
async def mulai_absen(_, message: Message):
    chat_id = message.chat.id
    if chat_id in absen_data:
        await message.reply_text("Sesi absen sudah berjalan!")
        return

    absen_data[chat_id] = {
        "start_time": datetime.now(),
        "participants": {}
    }
    await message.reply_text(
        "Sesi absen dimulai!\n\n"
        "Gunakan perintah /hadir untuk menandai kehadiran."
    )


# Perintah untuk menandai kehadiran
@app.on_message(filters.command("hadir") & filters.group & ~BANNED_USERS)
async def hadir(_, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.mention

    if chat_id not in absen_data:
        await message.reply_text("Belum ada sesi absen yang dimulai!")
        return

    if user_id in absen_data[chat_id]["participants"]:
        await message.reply_text(f"{user_name}, Anda sudah absen!")
        return

    absen_data[chat_id]["participants"][user_id] = {
        "name": user_name,
        "time": datetime.now().strftime("%H:%M:%S")
    }
    await message.reply_text(f"Terima kasih {user_name}, kehadiran Anda tercatat!")


# Perintah untuk melihat rekap absen
@app.on_message(filters.command("rekap") & filters.group & ~BANNED_USERS)
async def rekap_absen(_, message: Message):
    chat_id = message.chat.id
    if chat_id not in absen_data:
        await message.reply_text("Belum ada sesi absen yang dimulai!")
        return

    participants = absen_data[chat_id]["participants"]
    if not participants:
        await message.reply_text("Belum ada yang hadir di sesi absen ini.")
        return

    rekap = "Rekap Absen:\n\n"
    for idx, (user_id, data) in enumerate(participants.items(), start=1):
        rekap += f"{idx}. {data['name']} - {data['time']}\n"

    await message.reply_text(rekap)


# Perintah untuk menutup sesi absen
@app.on_message(filters.command("selesai") & filters.group & ~BANNED_USERS)
@admin_actual
async def selesai_absen(_, message: Message):
    chat_id = message.chat.id
    if chat_id not in absen_data:
        await message.reply_text("Belum ada sesi absen yang dimulai!")
        return

    participants = absen_data.pop(chat_id)["participants"]
    total = len(participants)

    rekapan_akhir = "Sesi absen ditutup!\n\n"
    rekapan_akhir += f"Total peserta hadir: {total}\n\n"

    if total > 0:
        rekapan_akhir += "Daftar kehadiran:\n"
        for idx, (user_id, data) in enumerate(participants.items(), start=1):
            rekapan_akhir += f"{idx}. {data['name']} - {data['time']}\n"
    else:
        rekapan_akhir += "Tidak ada yang hadir dalam sesi ini."

    await message.reply_text(rekapan_akhir)


# Perintah untuk mengatur mode pemutaran channel (opsional jika masih relevan dengan bot musik Anda)
@app.on_message(command("CHANNELPLAY_COMMAND") & filters.group & ~BANNED_USERS)
@admin_actual
async def playmode_(client, message: Message, _):
    try:
        lang_code = await get_lang(message.chat.id)
        CHANNELPLAY_COMMAND = get_command(lang_code)["CHANNELPLAY_COMMAND"]
    except Exception:
        CHANNELPLAY_COMMAND = get_command("id")["CHANNELPLAY_COMMAND"]

    if len(message.command) < 2:
        return await message.reply_text(
            _["cplay_1"].format(message.chat.title, CHANNELPLAY_COMMAND[0])
        )

    query = message.text.split(None, 2)[1].lower().strip()
    if (str(query)).lower() == "disable":
        await set_cmode(message.chat.id, None)
        return await message.reply_text("Channel Play Dimatikan")
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
            return await message.reply_text(
                "Bot tidak memiliki izin admin di saluran yang ditentukan."
            )
        except FloodWait as e:
            await asyncio.sleep(e.value)

        if creatorid != message.from_user.id:
            return await message.reply_text(
                _["cplay_6"].format(chat.title, creatorusername)
            )

        await set_cmode(message.chat.id, chat.id)
        return await message.reply_text(_["cplay_3"].format(chat.title, chat.id))