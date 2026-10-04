from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InputMediaDocument, Message
from PIL import Image
from datetime import datetime
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.utils import progress_for_pyrogram, humanbytes, convert
from helper.database import AshutoshGoswami24
from config import Config
import os
import time
import re
import subprocess
import asyncio

renaming_operations = {}

pattern1 = re.compile(r"S(\d+)(?:E|EP)(\d+)")
pattern2 = re.compile(r"S(\d+)\s*(?:E|EP|-\s*EP)(\d+)")
pattern3 = re.compile(r"(?:[([<{]?\s*(?:E|EP)\s*(\d+)\s*[)\]>}]?)")
pattern3_2 = re.compile(r"(?:\s*-\s*(\d+)\s*)")
pattern4 = re.compile(r"S(\d+)[^\d]*(\d+)", re.IGNORECASE)
patternX = re.compile(r"(\d+)")

pattern5 = re.compile(
    r"\b(?:.*?(\d{3,4}[^\dp]*p).*?|.*?(\d{3,4}p))\b",
    re.IGNORECASE
)
pattern6 = re.compile(r"[([<{]?\s*4k\s*[)\]>}]?", re.IGNORECASE)
pattern7 = re.compile(r"[([<{]?\s*2k\s*[)\]>}]?", re.IGNORECASE)
pattern8 = re.compile(r"[([<{]?\s*HdRip\s*[)\]>}]?|\bHdRip\b", re.IGNORECASE)
pattern9 = re.compile(r"[([<{]?\s*4kX264\s*[)\]>}]?", re.IGNORECASE)
pattern10 = re.compile(r"[([<{]?\s*4kx265\s*[)\]>}]?", re.IGNORECASE)


def extract_quality(filename):
    match5 = re.search(pattern5, filename)
    if match5:
        return match5.group(1) or match5.group(2)

    if re.search(pattern6, filename):
        return "4k"
    if re.search(pattern7, filename):
        return "2k"
    if re.search(pattern8, filename):
        return "HdRip"
    if re.search(pattern9, filename):
        return "4kX264"
    if re.search(pattern10, filename):
        return "4kx265"

    return "Unknown"


def extract_episode_number(filename):
    match = re.search(pattern1, filename)
    if match:
        return match.group(2)

    match = re.search(pattern2, filename)
    if match:
        return match.group(2)

    match = re.search(pattern3, filename)
    if match:
        return match.group(1)

    match = re.search(pattern3_2, filename)
    if match:
        return match.group(1)

    match = re.search(pattern4, filename)
    if match:
        return match.group(2)

    match = re.search(patternX, filename)
    if match:
        return match.group(1)

    return None


def extract_season_number(filename):
    match = re.search(
        r"\bS(\d+)(?=E|EP|\b)",
        filename,
        re.IGNORECASE
    )
    return match.group(1) if match else "01"


def extract_title(filename):
    name = os.path.splitext(os.path.basename(filename))[0]

    match = re.search(r"\s+S\d+\b", name, re.IGNORECASE)

    if match:
        title = name[:match.start()]
    else:
        title = name

    title = re.sub(r"[._]+", " ", title)
    title = re.sub(r"\s+", " ", title).strip(" -_")

    return title or "Unknown Title"


@Client.on_message(
    filters.private & (filters.document | filters.video | filters.audio)
)
async def auto_rename_files(client, message):
    user_id = message.from_user.id

    format_template = await AshutoshGoswami24.get_format_template(user_id)
    media_preference = await AshutoshGoswami24.get_media_preference(user_id)

    if not format_template:
        return await message.reply_text(
            "Please Set An Auto Rename Format First Using /autorename"
        )

    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        media_type = media_preference or "document"

    elif message.video:
        file_id = message.video.file_id
        file_name = f"{message.video.file_name or 'video'}.mp4"
        media_type = media_preference or "video"

    elif message.audio:
        file_id = message.audio.file_id
        file_name = f"{message.audio.file_name or 'audio'}.mp3"
        media_type = media_preference or "audio"

    else:
        return await message.reply_text("Unsupported File Type")

    if file_id in renaming_operations:
        elapsed_time = (
            datetime.now() - renaming_operations[file_id]
        ).seconds

        if elapsed_time < 10:
            return

    renaming_operations[file_id] = datetime.now()

    episode_number = extract_episode_number(file_name) or "01"
    season_number = extract_season_number(file_name)
    quality = extract_quality(file_name)
    title = extract_title(file_name)

    replacements = {
        "{title}": title,
        "{season}": season_number,
        "{episode}": str(episode_number),
        "{quality}": quality,
        "[episode]": "EP" + str(episode_number),
        "[quality]": quality,
    }

    for placeholder, value in replacements.items():
        format_template = format_template.replace(
            placeholder,
            value
        )

    _, file_extension = os.path.splitext(file_name)

    renamed_file_name = f"{format_template}{file_extension}"

    renamed_file_path = f"downloads/{renamed_file_name}"
    metadata_file_path = f"Metadata/{renamed_file_name}"

    os.makedirs(
        os.path.dirname(renamed_file_path),
        exist_ok=True
    )

    os.makedirs(
        os.path.dirname(metadata_file_path),
        exist_ok=True
    )

    download_msg = await message.reply_text(
        "Downloading the file..."
    )

    try:
        path = await client.download_media(
            message,
            file_name=renamed_file_path,
            progress=progress_for_pyrogram,
            progress_args=(
                "Download Started...",
                download_msg,
                time.time(),
            ),
        )

    except Exception as e:
        del renaming_operations[file_id]
        return await download_msg.edit(
            f"**Download Error:** {e}"
        )

    await download_msg.edit(
        "Renaming and Adding Metadata..."
    )

    ph_path = None

    try:
        os.rename(
            path,
            renamed_file_path
        )

        path = renamed_file_path

        metadata_added = False

        _bool_metadata = await AshutoshGoswami24.get_metadata(
            user_id
        )

        if _bool_metadata:
            metadata = await AshutoshGoswami24.get_metadata_code(
                user_id
            )

            if metadata:
                cmd = (
                    f'ffmpeg -i "{renamed_file_path}" '
                    f'-map 0 -c:s copy -c:a copy -c:v copy '
                    f'-metadata title="{metadata}" '
                    f'-metadata author="{metadata}" '
                    f'-metadata:s:s title="{metadata}" '
                    f'-metadata:s:a title="{metadata}" '
                    f'-metadata:s:v title="{metadata}" '
                    f'"{metadata_file_path}"'
                )

                try:
                    process = await asyncio.create_subprocess_shell(
                        cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )

                    stdout, stderr = await process.communicate()

                    if process.returncode == 0:
                        metadata_added = True
                        path = metadata_file_path
                    else:
                        error_message = stderr.decode()

                        await download_msg.edit(
                            f"**Metadata Error:**\n{error_message}"
                        )

                except Exception as e:
                    await download_msg.edit(
                        f"**Exception occurred:**\n{str(e)}"
                    )
                    return

        else:
            metadata_added = True

        if not metadata_added:
            await download_msg.edit(
                "Metadata addition failed. "
                "Uploading the renamed file only."
            )

            path = renamed_file_path

        upload_msg = await download_msg.edit(
            "Uploading the file..."
        )

        c_caption = await AshutoshGoswami24.get_caption(
            message.chat.id
        )

        c_thumb = await AshutoshGoswami24.get_thumbnail(
            message.chat.id
        )

        media_size = (
            message.document.file_size
            if message.document
            else message.video.file_size
            if message.video
            else message.audio.file_size
            if message.audio
            else 0
        )

        media_duration = (
            message.video.duration
            if message.video
            else message.audio.duration
            if message.audio
            else 0
        )

        caption = (
            c_caption.format(
                filename=renamed_file_name,
                filesize=humanbytes(media_size),
                duration=convert(media_duration or 0),
            )
            if c_caption
            else f"**{renamed_file_name}**"
        )

        if c_thumb:
            ph_path = await client.download_media(c_thumb)

        elif media_type == "video" and message.video.thumbs:
            ph_path = await client.download_media(
                message.video.thumbs[0].file_id
            )

        if ph_path:
            img = Image.open(ph_path).convert("RGB")
            img = img.resize((320, 320))
            img.save(ph_path, "JPEG")

        try:
            if media_type == "document":

                await client.send_document(
                    message.chat.id,
                    document=path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        "Upload Started...",
                        upload_msg,
                        time.time(),
                    ),
                )

            elif media_type == "video":

                await client.send_video(
                    message.chat.id,
                    video=path,
                    caption=caption,
                    thumb=ph_path,
                    duration=0,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        "Upload Started...",
                        upload_msg,
                        time.time(),
                    ),
                )

            elif media_type == "audio":

                await client.send_audio(
                    message.chat.id,
                    audio=path,
                    caption=caption,
                    thumb=ph_path,
                    duration=0,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        "Upload Started...",
                        upload_msg,
                        time.time(),
                    ),
                )

        except Exception as e:

            if os.path.exists(path):
                os.remove(path)

            if ph_path and os.path.exists(ph_path):
                os.remove(ph_path)

            return await upload_msg.edit(
                f"**Upload Error:** {e}"
            )

    except Exception as e:

        await download_msg.edit(
            f"**Error:** {e}"
        )

    finally:

        if os.path.exists(renamed_file_path):
            os.remove(renamed_file_path)

        if os.path.exists(metadata_file_path):
            os.remove(metadata_file_path)

        if ph_path and os.path.exists(ph_path):
            os.remove(ph_path)

        renaming_operations.pop(
            file_id,
            None
        )
