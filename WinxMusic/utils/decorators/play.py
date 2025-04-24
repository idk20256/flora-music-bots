    # Cek jika bot dalam mode maintenance
    if await is_maintenance() is False:
        if message.from_user.id not in SUDOERS:
            return

    # Cek jika mode bot pribadi diaktifkan
    if PRIVATE_BOT_MODE == str(True):
        if not await is_served_private_chat(message.chat.id):
            await message.reply_text(
                "**BOT MUSIK PRIBADI**\n\nHanya untuk obrolan resmi dari pemilik, minta pemilik saya untuk mengizinkan obrolan Anda terlebih dahulu."
            )
            return await app.leave_chat(message.chat.id)

    # Hapus perintah jika penghapusan perintah diaktifkan
    if await is_commanddelete_on(message.chat.id):
        try:
            await message.delete()
        except Exception:
            pass

    # Cek jika terdapat audio, video, atau URL
    audio_telegram = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    video_telegram = (
        (message.reply_to_message.video or message.reply_to_message.document)
        if message.reply_to_message
        else None
    )
    url = await Platform.youtube.url(message)
    if audio_telegram is None and video_telegram is None and url is None:
        if len(message.command) < 2:
            if "stream" in message.command:
                return await message.reply_text(_["str_1"])
            buttons = botplaylist_markup(_)
            return await message.reply_photo(
                photo=PLAYLIST_IMG_URL,
                caption=_["playlist_1"],
                reply_markup=InlineKeyboardMarkup(buttons),
            )

    # Proses untuk voice chat
    chat_id = message.chat.id
    try:
        is_call_active = (await app.get_chat(chat_id)).is_call_active
        if not is_call_active:
            return await message.reply_text(
                "**Tidak ditemukan obrolan video aktif**\n\nPastikan Anda memulai obrolan suara."
            )
    except Exception as e:
        print(f"Error saat memeriksa panggilan: {e}")

    # Cek apakah voice chat aktif
    if await is_active_chat(chat_id):
        userbot = await get_assistant(message.chat.id)
        try:
            call_participants_id = [
                member.chat.id
                async for member in userbot.get_call_members(chat_id)
                if member.chat
            ]
            if not call_participants_id or userbot.id not in call_participants_id:
                await Winx.stop_stream(chat_id)
        except ChannelPrivate:
            pass
        except RPCError as e:
            print(f"Error RPC: {e}")

    # Menjalankan perintah yang dimasukkan
    return await command(
        client,
        message,
        _,
        chat_id,
        None,
        None,
        None,
        url,
        None,
    )

return wrapper" dan menempelkan di file yang bernama apa