from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message
from WinxMusic import app  # Menggunakan instance bot utama

# Data absen
absen_data = {}

# Memulai sesi absen
@app.on_message(filters.command("absen") & filters.group)
async def mulai_absen(client, message: Message):
    chat_id = message.chat.id
    chat_name = message.chat.title  # Nama grup

    if chat_id in absen_data:
        await message.reply_text("Sesi absen sudah berjalan!")
        return

    absen_data[chat_id] = {
        "start_time": datetime.now(),
        "participants": {},
        "izin": {}  # Tambahkan data izin
    }

    current_time = datetime.now().strftime("%A, %d %B %Y")
    await message.reply_text(
        f"Sesi absen dimulai pada **{current_time}** di grup **{chat_name}**!\n\n"
        "Gunakan perintah /hadir untuk menandai kehadiran Anda.\n"
        "Gunakan perintah /izin <alasan> untuk mencatat izin.\n"
        "Gunakan perintah /selesai untuk mengakhiri sesi absen."
    )

# Mencatat kehadiran
@app.on_message(filters.command("hadir") & filters.group)
async def hadir_absen(_, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    if chat_id not in absen_data:
        await message.reply_text("Belum ada sesi absen yang dimulai! Gunakan /absen untuk memulai.")
        return

    if user_id in absen_data[chat_id]["participants"]:
        await message.reply_text("Anda sudah menandai kehadiran sebelumnya.")
        return

    waktu_hadir = datetime.now().strftime("%H:%M:%S")
    absen_data[chat_id]["participants"][user_id] = {
        "name": user_name,
        "time": waktu_hadir
    }
    await message.reply_text(f"{user_name}, kehadiran Anda telah dicatat pada {waktu_hadir}!")

# Mencatat izin dengan alasan
@app.on_message(filters.command("izin") & filters.group)
async def izin_absen(_, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    if chat_id not in absen_data:
        await message.reply_text("Belum ada sesi absen yang dimulai! Gunakan /absen untuk memulai.")
        return

    if user_id in absen_data[chat_id]["izin"]:
        await message.reply_text("Anda sudah mencatat izin sebelumnya.")
        return

    # Ambil alasan dari teks setelah perintah /izin
    alasan = " ".join(message.command[1:])
    if not alasan:
        await message.reply_text("Gunakan: /izin <alasan> untuk mencatat izin Anda.")
        return

    waktu_izin = datetime.now().strftime("%H:%M:%S")
    absen_data[chat_id]["izin"][user_id] = {
        "name": user_name,
        "reason": alasan,
        "time": waktu_izin
    }
    await message.reply_text(f"{user_name}, izin Anda telah dicatat dengan alasan: {alasan} pada {waktu_izin}.")

# Menyelesaikan sesi absen
@app.on_message(filters.command("selesai") & filters.group)
async def selesai_absen(client, message: Message):
    chat_id = message.chat.id
    chat_name = message.chat.title  # Nama grup

    if chat_id not in absen_data:
        await message.reply_text("Belum ada sesi absen yang dimulai!")
        return

    participants = absen_data[chat_id].pop("participants")
    izin_list = absen_data[chat_id].pop("izin")
    total_hadir = len(participants)
    total_izin = len(izin_list)

    current_time = datetime.now().strftime("%A, %d %B %Y")
    rekapan_akhir = f"**Daftar hadir pada {current_time} di grup {chat_name}:**\n\n"

    # Daftar Kehadiran
    if total_hadir > 0:
        rekapan_akhir += "> **Daftar Kehadiran:**\n"
        for idx, (user_id, data) in enumerate(participants.items(), start=1):
            rekapan_akhir += f"> {idx}. {data['name']} - {data['time']}\n"
        rekapan_akhir += ">\n>\n"
    else:
        rekapan_akhir += "> Tidak ada peserta yang hadir.\n\n"

    # Daftar Izin
    if total_izin > 0:
        rekapan_akhir += "> **Daftar Izin:**\n"
        for idx, (user_id, data) in enumerate(izin_list.items(), start=1):
            rekapan_akhir += f"> {idx}. {data['name']} - {data['time']} - Alasan: {data['reason']}\n"
        rekapan_akhir += ">\n>\n"
    else:
        rekapan_akhir += "> Tidak ada peserta yang mencatat izin.\n\n"

    rekapan_akhir += "*Gunakan perintah /selesai untuk mengakhiri sesi absen ini.*"
    await message.reply_text(rekapan_akhir)