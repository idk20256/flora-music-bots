import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message
from WinxMusic.utils.database import (
    setup_database, get_group_settings, update_group_settings,
    add_bl_word, remove_bl_word, get_blacklist_words
)

# Pastikan database sudah disiapkan saat modul dimuat
asyncio.create_task(setup_database())

# Perintah untuk mengaktifkan/menonaktifkan fitur anti-GCast
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

# Perintah untuk menambahkan kata ke blacklist
@app.on_message(filters.command("addbl", prefixes="/") & filters.group)
async def add_blacklist(client: Client, message: Message):
    chat_id = message.chat.id
    trigger = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not trigger:
        await message.reply("Silakan masukkan kata yang ingin ditambahkan ke blacklist.")
        return
    await add_bl_word(chat_id, trigger.lower())
    await message.reply(f"✅ Kata **{trigger}** berhasil ditambahkan ke blacklist.")

# Perintah untuk menghapus kata dari blacklist
@app.on_message(filters.command("delbl", prefixes="/") & filters.group)
async def remove_blacklist(client: Client, message: Message):
    chat_id = message.chat.id
    trigger = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not trigger:
        await message.reply("Silakan masukkan kata yang ingin dihapus dari blacklist.")
        return
    await remove_bl_word(chat_id, trigger.lower())
    await message.reply(f"✅ Kata **{trigger}** berhasil dihapus dari blacklist.")

# Perintah untuk menampilkan daftar blacklist
@app.on_message(filters.command("listbl", prefixes="/") & filters.group)
async def list_blacklist(client: Client, message: Message):
    chat_id = message.chat.id
    blacklist_words = await get_blacklist_words(chat_id)
    if not blacklist_words:
        await message.reply("Tidak ada kata yang di-blacklist.")
        return
    blacklist_text = "\n".join([f"- {word}" for word in blacklist_words])
    await message.reply(f"**Daftar Blacklist:**\n{blacklist_text}")

# Perintah untuk menambahkan pengguna ke whitelist
@app.on_message(filters.command("free", prefixes="/") & filters.group)
async def add_to_whitelist(client: Client, message: Message):
    chat_id = message.chat.id
    args = message.text.split(maxsplit=1)
    if len(args) < 2 and not message.reply_to_message:
        await message.reply("Silakan reply ke pesan pengguna atau masukkan ID/username untuk membebaskan pengguna.")
        return
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        username = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name
    else:
        target = args[1]
        if target.startswith("@"):
            user = await client.get_users(target)
            user_id = user.id
            username = user.username or user.first_name
        else:
            try:
                user_id = int(target)
                user = await client.get_users(user_id)
                username = user.username or user.first_name
            except ValueError:
                await message.reply("ID pengguna harus berupa angka valid.")
                return
    settings = await get_group_settings(chat_id)
    if "whitelist_users" not in settings:
        settings["whitelist_users"] = []
    if user_id not in settings["whitelist_users"]:
        settings["whitelist_users"].append(user_id)
        await update_group_settings(chat_id, settings)
        await message.reply(f"✅ Pengguna **{username}** (ID: `{user_id}`) telah dibebaskan dari respon bot.")
    else:
        await message.reply(f"Pengguna **{username}** (ID: `{user_id}`) sudah ada dalam daftar whitelist.")

# Perintah untuk menghapus pengguna dari whitelist
@app.on_message(filters.command("freeoff", prefixes="/") & filters.group)
async def remove_from_whitelist(client: Client, message: Message):
    chat_id = message.chat.id
    args = message.text.split(maxsplit=1)
    if len(args) < 2 and not message.reply_to_message:
        await message.reply("Silakan reply ke pesan pengguna atau masukkan ID/username untuk menghapus dari whitelist.")
        return
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        target = args[1]
        if target.startswith("@"):
            user = await client.get_users(target)
            user_id = user.id
        else:
            try:
                user_id = int(target)
            except ValueError:
                await message.reply("ID pengguna harus berupa angka valid.")
                return
    settings = await get_group_settings(chat_id)
    if "whitelist_users" in settings and user_id in settings["whitelist_users"]:
        settings["whitelist_users"].remove(user_id)
        await update_group_settings(chat_id, settings)
        await message.reply(f"✅ Pengguna dengan ID `{user_id}` telah dihapus dari whitelist.")
    else:
        await message.reply(f"Pengguna dengan ID `{user_id}` tidak ada dalam daftar whitelist.")

# Handler untuk memantau pesan di grup
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