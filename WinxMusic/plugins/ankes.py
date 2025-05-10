import asyncio
import re
from pyrogram import filters, Client
from pyrogram.types import Message
from WinxMusic.utils.database import (
    setup_database, get_group_settings, update_group_settings,
    add_bl_word, remove_bl_word, get_blacklist_words
)

# Pastikan database sudah disiapkan saat modul dimuat
asyncio.create_task(setup_database())

# Mengelola fitur Anti-GCast
@app.on_message(filters.command("ankes", prefixes="/") & filters.group)
async def ankes_toggle(client: Client, message: Message):
    chat_id = message.chat.id
    args = message.text.split(maxsplit=1)
    settings = await get_group_settings(chat_id)
    if len(args) < 2:
        status = "aktif" if settings.get("enabled", False) else "nonaktif"
        await message.reply(f"Fitur anti-GCast saat ini **{status}**.")
        return
    if args[1].lower() in ["on", "aktif"]:
        settings["enabled"] = True
        await update_group_settings(chat_id, settings)
        await message.reply("✅ Fitur anti-GCast telah **diaktifkan**.")
    elif args[1].lower() in ["off", "nonaktif"]:
        settings["enabled"] = False
        await update_group_settings(chat_id, settings)
        await message.reply("❌ Fitur anti-GCast telah **dinonaktifkan**.")
    else:
        await message.reply("Gunakan `/ankes on` untuk mengaktifkan atau `/ankes off` untuk menonaktifkan fitur.")

# Menambahkan kata ke blacklist
@app.on_message(filters.command("addbl", prefixes="/") & filters.group)
async def add_blacklist(client: Client, message: Message):
    chat_id = message.chat.id
    text = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not text:
        await message.reply("Silakan masukkan kata yang ingin ditambahkan ke blacklist.")
        return
    triggers = {trigger.strip().lower() for trigger in text.split("\n") if trigger.strip()}
    for trigger in triggers:
        await add_bl_word(chat_id, trigger)
    await message.reply(f"✅ Kata-kata berikut berhasil ditambahkan ke blacklist:\n\n{', '.join(triggers)}")

# Menghapus kata dari blacklist
@app.on_message(filters.command("delbl", prefixes="/") & filters.group)
async def remove_blacklist(client: Client, message: Message):
    chat_id = message.chat.id
    text = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not text:
        await message.reply("Silakan masukkan kata yang ingin dihapus dari blacklist.")
        return
    triggers = {trigger.strip().lower() for trigger in text.split("\n") if trigger.strip()}
    for trigger in triggers:
        await remove_bl_word(chat_id, trigger)
    await message.reply(f"✅ Kata-kata berikut berhasil dihapus dari blacklist:\n\n{', '.join(triggers)}")

# Menampilkan daftar blacklist
@app.on_message(filters.command("listbl", prefixes="/") & filters.group)
async def list_blacklist(client: Client, message: Message):
    chat_id = message.chat.id
    blacklist_words = await get_blacklist_words(chat_id)
    if not blacklist_words:
        await message.reply("Tidak ada kata yang di-blacklist.")
        return
    blacklist_text = "\n".join([f"- {word}" for word in blacklist_words])
    await message.reply(f"**Daftar Blacklist:**\n{blacklist_text}")

# Menambahkan pengguna ke whitelist
@app.on_message(filters.command("free", prefixes="/") & filters.group)
async def add_to_whitelist(client: Client, message: Message):
    # (Kode whitelist pengguna tetap sama seperti di `ankes.py`)

# Menghapus pengguna dari whitelist
@app.on_message(filters.command("freeoff", prefixes="/") & filters.group)
async def remove_from_whitelist(client: Client, message: Message):
    # (Kode whitelist pengguna tetap sama seperti di `ankes.py`)

# Handler untuk memantau pesan dan blacklist
@app.on_message(filters.group)
async def monitor_messages(client: Client, message: Message):
    chat_id = message.chat.id
    settings = await get_group_settings(chat_id)
    if not settings.get("enabled", False):
        return
    if message.from_user and message.from_user.is_bot:
        return
    if message.from_user and message.from_user.id in settings.get("whitelist_users", []):
        return
    text = (message.text or message.caption or "").lower()
    blacklist_words = await get_blacklist_words(chat_id)
    if any(word in text for word in blacklist_words):
        try:
            await message.delete()
        except Exception as e:
            print(f"Error saat menghapus pesan: {e}")
            
