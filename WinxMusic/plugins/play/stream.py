from pyrogram import filters
from pyrogram.types import Message
from pytgcalls.exceptions import NoActiveGroupCall

import config
from WinxMusic import app
from WinxMusic.core.call import Winx
from WinxMusic.utils.decorators.play import play_wrapper
from WinxMusic.utils.logger import play_logs
from WinxMusic.utils.stream.stream import stream
from config import BANNED_USERS
from strings import command


@app.on_message(command("STREAM_COMMAND") & filters.group & ~BANNED_USERS)
@play_wrapper
async def stream_command(
        client,
        message: Message,
        _,
        chat_id,
        video,
        channel,
        playmode,
        url,
        fplay,
):
    if url:
        mystic = await message.reply_text(
            _["play_2"].format(channel) if channel else _["play_1"]
        )
        try:
            await Winx.stream_call(url)
        except NoActiveGroupCall:
            await mystic.edit_text(
                "Ada masalah dengan bot. tolong laporkan ke Pemilik saya dan minta mereka untuk memeriksa grup logger"
            )
            text = "Harap Aktifkan obrolan suara.. Bot tidak dapat mengalirkan url.."
            return await app.send_message(config.LOG_GROUP_ID, text)
        except Exception as e:
            return await mystic.edit_text(_["general_3"].format(type(e).__name__))
        await mystic.edit_text(_["str_2"])
        try:
            await stream(
                _,
                mystic,
                message.from_user.id,
                url,
                chat_id,
                message.from_user.first_name,
                message.chat.id,
                video=True,
                streamtype="index",
            )
        except Exception as e:
            ex_type = type(e).__name__
            err = e if ex_type == "AssistantErr" else _["general_3"].format(ex_type)
            return await mystic.edit_text(err)
        return await play_logs(message, streamtype="M3u8 or Index Link")
    else:
        await message.reply_text(_["str_1"])
