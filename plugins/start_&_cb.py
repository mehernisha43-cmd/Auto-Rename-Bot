import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from helper.database import AshutoshGoswami24
from config import Config, Txt


# Start picture included in the bot project
START_PIC = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "helper",
    "start_pic.jpg"
)


def start_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📢 Updates",
                url="https://t.me/+1CcAFHLS2tU4YWVl"
            ),
            InlineKeyboardButton(
                "💬 Support",
                url="https://t.me/+1jDuhUQ41hA1YmVl"
            )
        ],
        [
            InlineKeyboardButton(
                "⚙️ Help",
                callback_data="help"
            ),
            InlineKeyboardButton(
                "💙 About",
                callback_data="about"
            )
        ],
        [
            InlineKeyboardButton(
                "🧑‍💻 Developer",
                url="https://t.me/TANJIROKAMADO404"
            )
        ]
    ])


@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user = message.from_user

    await AshutoshGoswami24.add_user(client, message)

    caption = Txt.START_TXT.format(
        user.first_name
    )

    # Use the uploaded ANIFLIX start picture
    if os.path.exists(START_PIC):
        await message.reply_photo(
            photo=START_PIC,
            caption=caption,
            reply_markup=start_buttons()
        )
    else:
        await message.reply_text(
            text=caption,
            reply_markup=start_buttons(),
            disable_web_page_preview=True
        )


@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):

    data = query.data
    await query.answer()

    if data == "home":

        caption = Txt.START_TXT.format(
            query.from_user.first_name
        )

        if os.path.exists(START_PIC):
            try:
                await query.message.delete()

                await client.send_photo(
                    chat_id=query.from_user.id,
                    photo=START_PIC,
                    caption=caption,
                    reply_markup=start_buttons()
                )
            except Exception:
                await query.message.edit_text(
                    caption,
                    reply_markup=start_buttons()
                )
        else:
            await query.message.edit_text(
                caption,
                reply_markup=start_buttons()
            )

    elif data == "help":

        await query.message.edit_text(
            Txt.HELP_TXT.format(client.mention),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⚙️ Setup AutoRename Format",
                        callback_data="file_names"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🖼️ Thumbnail",
                        callback_data="thumbnail"
                    ),
                    InlineKeyboardButton(
                        "✏️ Caption",
                        callback_data="caption"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🏠 Home",
                        callback_data="home"
                    )
                ]
            ])
        )

    elif data == "about":

        await query.message.edit_text(
            Txt.ABOUT_TXT,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 Back",
                        callback_data="home"
                    ),
                    InlineKeyboardButton(
                        "✖️ Close",
                        callback_data="close"
                    )
                ]
            ])
        )

    elif data == "caption":

        await query.message.edit_text(
            Txt.CAPTION_TXT,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 Back",
                        callback_data="help"
                    )
                ]
            ])
        )

    elif data == "thumbnail":

        await query.message.edit_text(
            Txt.THUMBNAIL_TXT,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 Back",
                        callback_data="help"
                    )
                ]
            ])
        )

    elif data == "file_names":

        format_template = await AshutoshGoswami24.get_format_template(
            query.from_user.id
        )

        await query.message.edit_text(
            Txt.FILE_NAME_TXT.format(
                format_template=format_template or "Not Set"
            ),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 Back",
                        callback_data="help"
                    )
                ]
            ])
        )

    elif data == "close":

        try:
            await query.message.delete()
        except Exception:
            pass
