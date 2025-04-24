import datetime

def log_debug_message(message: str):
    """
    Fungsi untuk mencetak pesan debug.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG] {timestamp} - {message}")


def log_error_message(error: Exception):
    """
    Fungsi untuk mencetak pesan error.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[ERROR] {timestamp} - {type(error).__name__}: {error}")


def log_info_message(message: str):
    """
    Fungsi untuk mencetak pesan informasi umum.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[INFO] {timestamp} - {message}")
