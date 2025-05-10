# WinxMusic/utils/error_handler.py
import traceback
from config import LOG_GROUP_ID

def suggest_fix(exc_type, exc_value, file_name, line_no):
    if exc_type.__name__ == "Key>{file_name}</code> baris <code>{line_no}</code>. "
            f"Gunakan <code>dict.get()</code> atau pastikan key ada."
        )
    elif exc_type.__name__ == "AttributeError":
        return (
            f"💡 <b>Solusi:</b> Past}</code> sudah punya atribut tersebut."
        )
    elif exc_type.__name__ == "TypeError":
        return (
            f"💡 <b>Solusi:</b> Cek tipe data pada file <code>{file_name}</code> baris <code>{line_no}</code>."
        )
    else:
        return "💡 <b>Solusi:</b> Cek kode pada lokasi error dan perbaiki sesuai traceback."

async def send_error_to_log_group(app, exc_type, exc_value, exc_traceback):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    try line_no = last_trace.lineno
    except Exception:
        file_name = "Tidak diketahui"
        line_no = "Tidak diketahui"
    solution = suggest_fix(exc_type, exc_value, file_name, line_no)
    text = (
        f"🚨 <b>Error Terdeteksi!</b>\n\n"
>\n"
        f"<b>Pesan:</b> <code>{exc_value}</code>\n"
        f"<b>Traceback:</b>\n<pre>{tb}</pre>\n\n"
        f"{solution}"
    )
    try:
        await app.send_message(
            LOG_GROUP_ID,
           ="html",
            disable_web_page_preview=True
        )
    except Exception as err:
        print("Gagal mengirim error ke log group:", err)
        print("Error asli:", tb)

def global_exception_handler(app):
    import sys
    import asyncio
    def handler(exc_type, exc_value, exc_traceback(app, exc_type, exc_value, exc_traceback)
        )
    sys.excepthook = handler