from WinxMusic import app
from WinxMusic.misc import SUDOERS
from WinxMusic.utils.database import autoend_off, autoend_on
from strings import command


@app.on_message(command("AUTOEND_COMMAND") & SUDOERS)
async def auto_end_stream(client, message):
    usage = "**ᴜsᴀɢᴇ:**\n\n/autoend [enable|disable]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    state = message.text.split(None, 1)[1].strip()
    state = state.lower()
    if state == "enable":
        await autoend_on()
        await message.reply_text(
            "Akhiri Otomatis diaktifkan.\n\n akan meninggalkan obrolan suara secara otomatis setelah 30 detik jika seseorang mendengarkan lagu dengan pesan peringatan.."
        )
    elif state == "disable":
        await autoend_off()
        await message.reply_text("Autoend dimatikan")
    else:
        await message.reply_text(usage)
