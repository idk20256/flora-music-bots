import traceback
from config import LOG_GROUP_ID

async def send_error_to_log_group(app, exc_type, exc_value, exc_traceback):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    await app.send_message(
        LOG_GROUP_ID,
        f"🚨 Error!\nType: {exc_type}\nValue: {exc_value}\nTraceback:\n{tb}"
    )

def global_exception_handler(exc_type, exc_value, exc_traceback):
    # Bisa tambahkan logic lebih lanjut di sini
    print("Ada error:", exc_type, exc_value)
    # Contoh: Kirim ke log group (jika context app tersedia)