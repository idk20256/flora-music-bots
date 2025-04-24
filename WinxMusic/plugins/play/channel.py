async def handle_channel_play(client, message: Message, _, CHANNELPLAY_COMMAND):
    # Memastikan perintah memiliki argumen
    if len(message.command) < 2:
        return await message.reply_text(
            _["cplay_1"].format(message.chat.title, CHANNELPLAY_COMMAND[0])
        )
    query = message.text.split(None, 2)[1].lower().strip()

    if query == "disable":
        # Nonaktifkan mode channel
        await set_cmode(message.chat.id, None)
        return await message.reply_text("Channel Play Dimatikan")

    elif query == "linked":
        # Gunakan kanal terkait (linked chat)
        chat = await app.get_chat(message.chat.id)
        if chat.linked_chat:
            chat_id = chat.linked_chat.id
            # Pastikan bot memiliki izin di kanal terkait
            try:
                bot_member = await app.get_chat_member(chat_id, client.me.id)
                if not bot_member.can_post_messages:
                    return await message.reply_text("Bot tidak memiliki izin untuk posting di kanal terkait.")
            except Exception:
                return await message.reply_text("Gagal memeriksa izin bot di kanal terkait.")
                
            await set_cmode(message.chat.id, chat_id)
            return await message.reply_text(
                _["cplay_3"].format(chat.linked_chat.title, chat.linked_chat.id)
            )
        else:
            return await message.reply_text(_["cplay_2"])

    else:
        # Periksa kanal manual berdasarkan input pengguna
        try:
            chat = await app.get_chat(query)
        except Exception:
            return await message.reply_text(_["cplay_4"])
        
        if chat.type != ChatType.CHANNEL:
            return await message.reply_text(_["cplay_5"])

        try:
            bot_member = await app.get_chat_member(chat.id, client.me.id)
            if not bot_member.can_post_messages:
                return await message.reply_text("Bot tidak memiliki izin untuk posting di kanal ini.")
        except Exception:
            return await message.reply_text("Gagal memeriksa izin bot di kanal.")

        # Periksa apakah pengguna adalah pemilik kanal
        try:
            admins = app.get_chat_members(chat.id, filter=ChatMembersFilter.ADMINISTRATORS)
        except Exception:
            return await message.reply_text(_["cplay_4"])
        
        creator_id = None
        async for users in admins:
            if users.status == ChatMemberStatus.OWNER:
                creator_id = users.user.id
                break

        if creator_id != message.from_user.id:
            return await message.reply_text(
                _["cplay_6"].format(chat.title, chat.username or "unknown")
            )

        # Aktifkan mode channel
        await set_cmode(message.chat.id, chat.id)
        return await message.reply_text(_["cplay_3"].format(chat.title, chat.id))
