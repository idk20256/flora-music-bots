import traceback
from config import LOG_GROUP_ID

async def send_error_to_log_group(app, exc_type, exc_value, exc_traceback):
    """
    Mengirim detail error ke grup log Telegram.
    """
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    # Ambil info baris & file terakhir error
    last_trace = traceback.extract_tb(exc_traceback)[-1]
    file_name = last_trace.filename
    line_no = last_trace.lineno
    text = (
        f"🚨 <b>Error Terdeteksi!</b>\n\n"
        f"<b>File</b>: <code>{file_name}</code>\n"
        f"<b>Baris</b>: <code>{line_no}</code>\n"
        f"<b>Type</b>: <code>{exc_type.__name__}</code>\n"
        f"<b>Pesan</b>: <code>{exc_value}</code>\n\n"
        f"<b>Traceback:</b>\n<pre>{tb}</pre>"
    )
    try:
        await app.send_message(
            LOG_GROUP_ID,
            text,
            parse_mode="html",
            disable_web_page_preview=True
        )
    except Exception as err:
        print("Gagal mengirim error ke log group:", err)
        print("Error asli:", tb)

def suggest_fix(exc_type, exc_value, file_name, line_no):
    """Memberikan saran solusi berdasarkan tipe error."""
    if exc_type.__name__ == "KeyError":
        return (
            f"💡 <b>Solusi:</b>\n"
            f"Cek file <code>{file_name}</code> pada baris <code>{line_no}</code>.\n"
            f"Pastikan key yang diakses di dict sudah ada, atau gunakan <code>.get()</code>."
        )
    elif exc_type.__name__ == "AttributeError":
        return (
            f"💡 <b>Solusi:</b>\n"
            f"Cek file <code>{file_name}</code> pada baris <code>{line_no}</code>.\n"
            f"Pastikan objek sudah memiliki atribut tersebut sebelum diakses."
        )
    elif exc_type.__name__ == "TypeError":
        return (
            f"💡 <b>Solusi:</b>\n"
            f"Cek file <code>{file_name}</code> pada baris <code>{line_no}</code>.\n"
            f"Periksa tipe data variabel yang digunakan."
        )
    else:
        return (
            "💡 <b>Solusi:</b>\nCek kembali kode pada lokasi error dan perbaiki sesuai traceback."
        )

def global_exception_handler(app):
    """
    Handler global yang akan menangkap uncaught exception lalu mengirim ke grup log.
    """
    import sys
    import asyncio
    def handler(exc_type, exc_value, exc_traceback):
        # Print ke console
        print("Exception caught:", exc_type, exc_value)
        # Siapkan text notifikasi
        try:
            last_trace = traceback.extract_tb(exc_traceback)[-1]
            file_name = last_trace.filename
            line_no = last_trace.lineno
        except Exception:
            file_name = "Tidak diketahui"
            line_no = "Tidak diketahui"
        solution = suggest_fix(exc_type, exc_value, file_name, line_no)
        # Kirim ke grup log secara async
        tb = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        error_text = (
            f"🚨 <b>Error Terdeteksi!</b>\n\n"
            f"<b>File</</b>: <code>{line_no}</code>\n"
            f"<b>Type</b>: <code>{exc_type.__name__}</code>\n"
            f"<b>Pesan</b>: <code>{exc_value}</code>\n\n"
            f"<b>Traceback:</b>\n<pre>{tb}</pre>\n\n"
            f"{solution}"
        )
        try:
            asyncio.create_task(
                app.send_message(
                    LOG_GROUP_ID,
                    error_text,
                    parse_mode="html",
                    disable_web_page_preview=True
                )
            )
        except Exception as err:
            print("Gagal mengirim error ke log group:", err)
    sys.excepthook = handler