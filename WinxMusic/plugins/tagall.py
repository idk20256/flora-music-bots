import asyncio
import random
import re
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait
from WinxMusic import app

# Daftar emoji standar
EMOJI_LIST = ["😀", "🎉", "🔥", "🌟", "💥", "✨", "❤️", "🎵", "🌈", "🍀", "🎈", "🌼", "☀️"]

# Daftar emoji premium
PREMIUM_EMOJI_LIST = ["✨🔥", "🌟🌈", "💎🎉", "🎵🎶", "🔮❤️"]

SPAM_CHATS = []

# Regex untuk mendeteksi URL
URL_REGEX = r"(https?://[^\s]+)"

async def is_admin(chat_id, user_id):
    admin_ids = [
        admin.user.id
        async for admin in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS)
    ]
    return user_id in admin_ids

@app.on_message(filters.command(["all", "allmention", "mentionall", "tagall"], prefixes=["/", "@"]))
async def tag_all_users(_, message):
    admin = await is_admin(message.chat.id, message.from_user.id)
    if not admin:
        return

    if message.chat.id in SPAM_CHATS:
        return await message.reply_text(
            "<blockquote><b>Tag all sedang berjalan der, ketik /cancel untuk membatalkan der</b></blockquote>"
        )
    
    replied = message.reply_to_message
    if len(message.command) < 2 and not replied:
        await message.reply_text(
            "<blockquote><b>Kasih teks nya der\n/tagall Hi Nikol ganteng</b></blockquote>"
        )
        return

    # Ambil teks dari perintah
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else ""
    
    # Deteksi URL dalam teks
    url_match = re.search(URL_REGEX, text)
    if url_match:
        url = url_match.group(0)
        # Format URL agar terlihat lebih menonjol
        text = text.replace(url, f"[Klik Disini]({url})")

    # Escape karakter khusus untuk MarkdownV2
    text = text.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]").replace("(", "\\(").replace(")", "\\)").replace("~", "\\~").replace("`", "\\`").replace(">", "\\>").replace("#", "\\#").replace("+", "\\+").replace("-", "\\-").replace("=", "\\=").replace("|", "\\|").replace("{", "\\{").replace("}", "\\}").replace(".", "\\.").replace("!", "\\!")

    usernum = 0
    usertxt = ""
    SPAM_CHATS.append(message.chat.id)
    try:
        async for m in app.get_chat_members(message.chat.id):
            if message.chat.id not in SPAM_CHATS:
                break
            if m.user.is_deleted or m.user.is_bot:
                continue

            # Gunakan emoji premium jika user memiliki Telegram Premium
            if m.user.is_premium:
                random_emoji = random.choice(PREMIUM_EMOJI_LIST)
            else:
                random_emoji = random.choice(EMOJI_LIST)

            usernum += 1
            usertxt += f"{random_emoji} "
            if usernum == 7:
                if replied:
                    await replied.reply_text(
                        f"{text}\n\n{usertxt}",
                        disable_web_page_preview=True,
                        parse_mode="MarkdownV2",
                    )
                else:
                    await app.send_message(
                        message.chat.id,
                        f"{text}\n\n{usertxt}",
                        disable_web_page_preview=True,
                        parse_mode="MarkdownV2",
                    )
                await asyncio.sleep(1)
                usernum = 0
                usertxt = ""

        if usernum != 0:
            if replied:
                await replied.reply_text(
                    f"{text}\n\n{usertxt}",
                    disable_web_page_preview=True,
                    parse_mode="MarkdownV2",
                )
            else:
                await app.send_message(
                    message.chat.id,
                    f"{text}\n\n{usertxt}",
                    disable_web_page_preview=True,
                    parse_mode="MarkdownV2",
                )
    except FloodWait as e:
        await asyncio.sleep(e.value)
    finally:
        try:
            SPAM_CHATS.remove(message.chat.id)
        except Exception:
            pass

@app.on_message(
    filters.command(["stopmention", "cancel", "cancelmention", "offmention", "mentionoff", "cancelall"], prefixes=["/", "@"])
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
        return await message.reply_text("<blockquote><b>Tag all sukses dihentikan der</b></blockquote>")
    else:
        await message.reply_text("<blockquote><b>Gak ada proses berjalan der</b></blockquote>")
        return

__MODULE__ = "Tagall"
__HELP__ = """
<blockquote><b>Admin Only
/tagall - Tag all semua member grup lu der
/cancel - Cancel tag all yang sedang berjalan der</b></blockquote>
"""