import re
import os
import time

id_pattern = re.compile(r'^.\d+$')


class Config(object):
    # Pyrogram client config
    API_ID = int(os.environ.get("API_ID", "0") or "0")
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

    # Database config
    DB_NAME = os.environ.get("DB_NAME", "autorename")
    DB_URL = os.environ.get("DB_URL", "")

    # Other configs
    BOT_UPTIME = time.time()
    START_PIC = os.environ.get("START_PIC", "")

    ADMIN = []
    for admin in re.split(r"[\s,]+", os.environ.get("ADMIN", "").strip()):
        if admin:
            try:
                ADMIN.append(int(admin))
            except ValueError:
                ADMIN.append(admin.lstrip("@"))

    # Force Subscribe
    FORCE_SUB_CHANNELS = [
        x.strip().lstrip("@")
        for x in (
            os.environ.get("FORCE_SUB_CHANNELS")
            or os.environ.get("FORCE_SUB")
            or ""
        ).split(",")
        if x.strip()
    ]

    # Log channel
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0") or "0")

    # Web server
    PORT = int(os.environ.get("PORT", "8080") or "8080")

    WEBHOOK = (
        os.environ.get("WEBHOOK", "True")
        .strip()
        .lower()
        in {"1", "true", "yes", "on"}
    )


class Txt(object):

    START_TXT = """👋 Hello {}!

➻ Advanced Auto Rename Bot
➻ Custom Thumbnail & Caption
➻ Use /tutorial To Get Started

⚡ Powered By @ANIFLIXANIMETAMIL
👨‍💻 Developer: @TANJIROKAMADO404
"""

    FILE_NAME_TXT = """<b><u>SETUP AUTO RENAME FORMAT</u></b>

Use These Keywords To Setup Custom File Name

✓ `{{title}}` :- Anime / Movie title
✓ `{{season}}` :- Season number
✓ `{{episode}}` :- Episode number
✓ `{{quality}}` :- Video resolution

<b>➻ Example :</b>
<code>/autorename {{title}} S{{season}} Ep{{episode}} [{{quality}}] [TAMIL]</code>

<b>➻ Your Current Auto Rename Format :</b>
<code>{format_template}</code>"""

    ABOUT_TXT = """<b>🤖 My Name :</b> ANIFLIX RENAME BOT ⚡
<b>📝 Language :</b> Python 3
<b>📚 Library :</b> Pyrogram 2.0
<b>🚀 Server :</b> Railway
<b>📢 Channel :</b> @ANIFLIXANIMETAMIL
<b>🧑‍💻 Developer :</b> @TANJIROKAMADO404

<b>♻️ Bot Made By :</b> @TANJIROKAMADO404"""

    # Metadata
    META_TXT = """<b>🎬 HOW TO SET METADATA</b>

Use these commands to set your metadata:

➻ /settitle - Set video title
➻ /setauthor - Set author
➻ /setartist - Set artist
➻ /setaudio - Set audio title
➻ /setsubtitle - Set subtitle title
➻ /setvideo - Set video title

Example:
<code>/settitle Naruto Shippuden</code>

After setting the metadata, use /metadata to turn metadata On or Off."""

    SEND_METADATA = "<b>Send the metadata text you want to use.</b>"

    THUMBNAIL_TXT = """<b><u>🖼️ HOW TO SET THUMBNAIL</u></b>

⦿ Send a photo to the bot to set your custom thumbnail.
⦿ /viewthumb - View your thumbnail
⦿ /delthumb - Delete your thumbnail"""

    CAPTION_TXT = """<b><u>📝 HOW TO SET CAPTION</u></b>

⦿ /set_caption - Set your caption
⦿ /see_caption - View your caption
⦿ /del_caption - Delete your caption"""

    PROGRESS_BAR = """<b>
╭━━━━❰ᴘʀᴏɢʀᴇss ʙᴀʀ❱━➣
┣⪼ 🗃️ Sɪᴢᴇ: {1} | {2}
┣⪼ ⏳️ Dᴏɴᴇ : {0}%
┣⪼ 🚀 Sᴩᴇᴇᴅ: {3}/s
┣⪼ ⏰️ Eᴛᴀ: {4}
╰━━━━━━━━━━━━━━━➣ </b>"""

    DONATE_TXT = """<b>💬 Need Help?</b>

For any issues with the bot, contact the developer.

<b>🧑‍💻 Developer:</b> @TANJIROKAMADO404
<b>📢 Updates:</b> https://t.me/+1CcAFHLS2tU4YWVl
<b>💬 Support:</b> https://t.me/+1jDuhUQ41hA1YmVl"""

    HELP_TXT = """<b>Hey</b> {} 👋

Use the buttons below to configure your Auto Rename Bot.

⚙️ <b>Metadata</b>
/metadata - Manage media metadata
/settitle - Set video title
/setauthor - Set author
/setartist - Set artist
/setaudio - Set audio title
/setsubtitle - Set subtitle
/setvideo - Set video metadata

⚠️ For any issues, contact @TANJIROKAMADO404"""
