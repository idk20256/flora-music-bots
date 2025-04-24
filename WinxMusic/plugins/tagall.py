import asyncio
import random
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait
from WinxMusic import app

# Daftar emoji acak
EMOJI_LIST = ["😀", "🎉", "🔥", "🌟", "💥", "✨", "❤️", "🎵", "🌈", "🍀", "🎈", "☀️"]

SPAM_CHATS = []


async def is_admin(chat_id, user_id):
    admin_ids = [
        admin.user.id
        async for admin in app.get_chat_members(
            chat_id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]
    return user_id in admin_ids


@app.on_message(
    filters.command(["all", "allmention", "mentionall", "tagall"], prefixes=["/", "@"])
)
async def tag_all_users(_, message):
    admin = await is_admin(message.chat.id, message.from_user.id)
    if not admin:
        return

    if message.chat.id in SPAM_CHATS:
        return await message.reply_text(
            "Tag all sedang berjalan. Ketik /cancel untuk membatalkannya."
        )

    replied = message.reply_to_message
    if len(message.command) < 2 and not replied:
        await message.reply_text(
            "Kasih teksnya der\nContoh: /tagall Halo semuanya!"
        )
        return

    usernum = 0
    usertxt = ""
    SPAM_CHATS.append(message.chat.id)

    try:
        async for m in app.get_chat_members(message.chat.id):
            if message.chat.id not in SPAM_CHATS:
                break
            if m.user.is_deleted or m.user.is_bot:
                continue

            # Tambahkan emoji acak
            emoji = random.choice(EMOJI_LIST)
            usernum += 1
            usertxt += f"{emoji} "

            # Kirim pesan setiap 7 pengguna
            if usernum == 7:
                if replied:
                    await replied.reply_text(
                        usertxt,
                        disable_web_page_preview=True,
                    )
                else:
                    text = message.text.split(None, 1)[1]
                    await app.send_message(
                        message.chat.id,
                        f"{text}\n\n{usertxt}",
                        disable_web_page_preview=True,
                    )
                await asyncio.sleep(1)
                usernum = 0
                usertxt = ""

        # Kirim sisa pengguna
        if usernum != 0:
            if replied:
                await replied.reply_text(
                    usertxt,
                    disable_web_page_preview=True,
                )
            else:
                text = message.text.split(None, 1)[1]
                await app.send_message(
                    message.chat.id,
                    f"{text}\n\n{usertxt}",
                    disable_web_page_preview=True,
                )

    except FloodWait as e:
        await asyncio.sleep(e.value)
    finally:
        try:
            SPAM_CHATS.remove(message.chat.id)
        except Exception:
            pass


@app.on_message(
    filters.command(
        ["stopmention", "cancel", "cancelmention", "offmention", "mentionoff", "cancelall"],
        prefixes=["/", "@"],
    )
)
async def cancelcmd(_, message):
    chat_id = message.chat.id
    admin = await is_admin(chat_id, message.from_user.id)
    if not admin:
        return
    if chat_id in SPAM_CHATS:
        try:
            SPAM_CHATS.remove(chat_id)
        except Exception:
            pass
        return await message.reply_text("Tag all sukses dihentikan der.")
    else:
        await message.reply_text("Gak ada proses berjalan der.")
        return


__MODULE__ = "Tagall"
__HELP__ = """
Admin Only
/tagall - Tag all semua member grup dengan emoji
/cancel - Cancel tag all yang sedang berjalan
"""