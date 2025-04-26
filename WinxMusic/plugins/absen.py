# Menyelesaikan sesi absen
@app.on_message(filters.command("selesai") & filters.group)
async def selesai_absen(client, message: Message):
    chat_id = message.chat.id
    chat_name = message.chat.title  # Nama grup

    # Periksa apakah sesi absen telah dimulai
    if chat_id not in absen_data or "participants" not in absen_data[chat_id]:
        await message.reply_text("Belum ada sesi absen yang dimulai!")
        return

    # Ambil data peserta dan izin
    participants = absen_data[chat_id].pop("participants", {})
    izin_list = absen_data[chat_id].pop("izin", {})
    total_hadir = len(participants)
    total_izin = len(izin_list)

    current_time = datetime.now().strftime("%A, %d %B %Y")
    rekapan_akhir = f"**Rekapan absen pada {current_time} di grup {chat_name}:**\n\n"

    # Daftar Kehadiran
    if total_hadir > 0:
        rekapan_akhir += "\"Daftar Kehadiran:\"\n"
        for idx, (user_id, data) in enumerate(participants.items(), start=1):
            rekapan_akhir += f"{idx}. {data['name']} - {data['time']}\n"
        rekapan_akhir += "\n"
    else:
        rekapan_akhir += "\"Daftar Kehadiran:\"\nTidak ada peserta yang hadir.\n\n"

    # Daftar Izin
    if total_izin > 0:
        rekapan_akhir += "\"Daftar Izin:\"\n"
        for idx, (user_id, data) in enumerate(izin_list.items(), start=1):
            rekapan_akhir += f"{idx}. {data['name']} - {data['time']} - Alasan: {data['reason']}\n"
        rekapan_akhir += "\n"
    else:
        rekapan_akhir += "\"Daftar Izin:\"\nTidak ada peserta yang mencatat izin.\n\n"

    # Tambahkan pemberitahuan bahwa absen telah selesai
    rekapan_akhir += "**Sesi absen telah selesai. Terima kasih atas partisipasinya!**"
    await message.reply_text(rekapan_akhir)