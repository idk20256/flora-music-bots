from datetime import datetime, timedelta
from re import findall
from re import sub as re_sub

from pyrogram import errors
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message

MARKDOWN = """
Bacalah teks di bawah ini dengan saksama untuk mengetahui cara kerja pemformatan!

<u>Isi yang didukung:</u>

{GROUPNAME} - Nama grup
{NAME} - Nama pengguna
{ID} - ID Pengguna
{FIRSTNAME} - Nama depan pengguna
{SURNAME} - Jika pengguna memiliki nama keluarga, ini akan menampilkan nama keluarga, jika tidak, tidak ada apa pun
{USERNAME} - Nama pengguna pengguna

{TIME} - Waktu saat ini
{DATE} - Tanggal saat ini
{WEEKDAY} - Hari saat ini dalam seminggu

<b><u>CATATAN:</u></b> Isian hanya berfungsi di modul selamat datang.

<u>Format yang didukung:</u>

<code>**bold**</code>: Ini akan muncul sebagai teks <b>Tebal</b>.
<code>~~strikethrough~~</code>: Ini akan muncul sebagai teks <strike>strikethrough</strike>.
<code>__italic__</code>: Ini akan muncul sebagai teks <i>miring</i>.
<code>--underline--</code>: Ini akan muncul sebagai teks <u>bergaris bawah</u>.
<code>`code`</code>: Ini akan muncul sebagai teks <code>kode</code>.
<code>||spoiler||</code>: Ini akan muncul sebagai teks <spoiler>Spoiler</spoiler>.
<code>[hyperlink](google.com)</code>: Ini akan membuat <a href='https://www.google.com'>hyperlink</a>.
<code>>halo</code>: Ini akan muncul sebagai <blockquote>halo</blockquote>.
<b>Catatan:</b> Anda dapat menggunakan tag Markdown atau HTML.


<u>Pemformatan tombol:</u>

-> <blockquote>teks ~ [teks tombol, tautan tombol]</blockquote>


<u>Contoh:</u>

<b>Contoh</b>  
<blockquote><i>tombol dengan markdown</i> <code>format</code> ~ [teks tombol, https://google.com]</blockquote>
"""
WELCOMEHELP = """
/setwelcome - Balas pesan ini yang berisi format yang benar untuk pesan selamat datang, periksa akhir pesan ini.

/delwelcome - Menghapus pesan selamat datang.
/getwelcome - Menampilkan pesan selamat datang.

<b>SET SELAMAT DATANG -></b>

<b>Untuk menetapkan foto atau GIF sebagai pesan selamat datang Anda, tambahkan pesan selamat datang Anda sebagai keterangan foto atau GIF. Judul harus dalam format berikut.</b>

Untuk pesan selamat datang dalam bentuk teks, cukup kirimkan teksnya. Lalu tanggapi dengan perintah.

Formatnya harus seperti berikut:

{GROUPNAME} - Nama grup
{NAME} - Nama depan + nama belakang pengguna
{ID} - ID Pengguna
{FIRSTNAME} - Nama depan pengguna
{SURNAME} - Jika pengguna memiliki nama keluarga, ini akan menampilkan nama keluarga, jika tidak, tidak ada apa pun
{USERNAME} - Nama pengguna pengguna

{TIME} - Waktu saat ini
{DATE} - Tanggal saat ini
{WEEKDAY} - Hari saat ini dalam seminggu

~ #Pemisah ini (~) harus berada di antara teks dan tombol, hapus juga komentar ini.

tombol=[Bebek, https://duckduckgo.com]
tombol2=[Github, https://github.com]

<b>CATATAN-></b>

Periksa /markdownhelp untuk informasi lebih lanjut tentang pemformatan dan sintaksis lainnya.
"""


def get_urls_from_text(text: str) -> bool:
    regex = r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]
                [.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(
                \([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\
                ()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""".strip()
    return [x[0] for x in findall(regex, str(text))]


def extract_text_and_keyb(ikb, text: str, row_width: int = 2):
    keyboard = {}
    try:
        text = text.strip()
        if text.startswith("`"):
            text = text[1:]
        if text.endswith("`"):
            text = text[:-1]

        if "~~" in text:
            text = text.replace("~~", "¤¤")
        text, keyb = text.split("~")
        if "¤¤" in text:
            text = text.replace("¤¤", "~~")

        keyb = findall(r"\[.+\,.+\]", keyb)
        for btn_str in keyb:
            btn_str = re_sub(r"[\[\]]", "", btn_str)
            btn_str = btn_str.split(",")
            btn_txt, btn_url = btn_str[0], btn_str[1].strip()

            if not get_urls_from_text(btn_url):
                continue
            keyboard[btn_txt] = btn_url
        keyboard = ikb(keyboard, row_width)
    except Exception:
        return
    return text, keyboard


async def check_format(ikb, raw_text: str):
    keyb = findall(r"\[.+\,.+\]", raw_text)
    if keyb and not "~" in raw_text:
        raw_text = raw_text.replace("button=", "\n~\nbutton=")
        return raw_text
    if "~" in raw_text and keyb:
        if not extract_text_and_keyb(ikb, raw_text):
            return ""
        else:
            return raw_text
    else:
        return raw_text


async def get_data_and_name(replied_message, message):
    text = message.text.markdown if message.text else message.caption.markdown
    name = text.split(None, 1)[1].strip()
    text = name.split(" ", 1)
    if len(text) > 1:
        name = text[0]
        data = text[1].strip()
        if replied_message and (replied_message.sticker or replied_message.video_note):
            data = None
    else:
        if replied_message and (replied_message.sticker or replied_message.video_note):
            data = None
        elif (
                replied_message and not replied_message.text and not replied_message.caption
        ):
            data = None
        else:
            data = (
                replied_message.text.markdown
                if replied_message.text
                else replied_message.caption.markdown
            )
            command = message.command[0]
            match = f"/{command} " + name
            if not message.reply_to_message and message.text:
                if match == data:
                    data = "error"
            elif not message.reply_to_message and not message.text:
                if match == data:
                    data = None
    return data, name


async def extract_userid(message, text: str):
    """
    NOT TO BE USED OUTSIDE THIS FILE
    """

    def is_int(text: str):
        try:
            int(text)
        except ValueError:
            return False
        return True

    text = text.strip()

    if is_int(text):
        return int(text)

    entities = message.entities
    app = message._client
    if len(entities) < 2:
        return (await app.get_users(text)).id
    entity = entities[1]
    if entity.type == MessageEntityType.MENTION:
        return (await app.get_users(text)).id
    if entity.type == MessageEntityType.TEXT_MENTION:
        return entity.user.id
    return None


async def extract_user_and_reason(message, sender_chat=False):
    args = message.text.strip().split()
    text = message.text
    user = None
    reason = None

    try:
        if message.reply_to_message:
            reply = message.reply_to_message
            if not reply.from_user:
                if (
                        reply.sender_chat
                        and reply.sender_chat != message.chat.id
                        and sender_chat
                ):
                    id_ = reply.sender_chat.id
                else:
                    return None, None
            else:
                id_ = reply.from_user.id

            if len(args) < 2:
                reason = None
            else:
                reason = text.split(None, 1)[1]
            return id_, reason

        # if not reply to a message and no reason is given
        if len(args) == 2:
            user = text.split(None, 1)[1]
            return await extract_userid(message, user), None

        # if reason is given
        if len(args) > 2:
            user, reason = text.split(None, 2)[1:]
            return await extract_userid(message, user), reason

        return user, reason

    except errors.UsernameInvalid:
        return "", ""


async def extract_user(message):
    return (await extract_user_and_reason(message))[0]


def get_file_id_from_message(
        message,
        max_file_size=3145728,
        mime_types=["image/png", "image/jpeg"],
):
    file_id = None
    if message.document:
        if int(message.document.file_size) > max_file_size:
            return

        mime_type = message.document.mime_type

        if mime_types and mime_type not in mime_types:
            return
        file_id = message.document.file_id

    if message.sticker:
        if message.sticker.is_animated:
            if not message.sticker.thumbs:
                return
            file_id = message.sticker.thumbs[0].file_id
        else:
            file_id = message.sticker.file_id

    if message.photo:
        file_id = message.photo.file_id

    if message.animation:
        if not message.animation.thumbs:
            return
        file_id = message.animation.thumbs[0].file_id

    if message.video:
        if not message.video.thumbs:
            return
        file_id = message.video.thumbs[0].file_id
    return file_id


async def time_converter(message: Message, time_value: str) -> Message | datetime:
    unit = ["m", "h", "d"]
    check_unit = "".join(list(filter(time_value[-1].lower().endswith, unit)))
    currunt_time = datetime.now()
    time_digit = time_value[:-1]
    if not time_digit.isdigit():
        return await message.reply_text("Waktu yang ditentukan salah.")
    if check_unit == "m":
        temp_time = currunt_time + timedelta(minutes=int(time_digit))
    elif check_unit == "h":
        temp_time = currunt_time + timedelta(hours=int(time_digit))
    elif check_unit == "d":
        temp_time = currunt_time + timedelta(days=int(time_digit))
    else:
        return await message.reply_text("Waktu yang ditentukan salah.")
    return temp_time
