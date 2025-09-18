from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👨‍💻 Developer", url=f"https://t.me/bohd4nx")],
            [InlineKeyboardButton(text="📖 How to Use", callback_data="help")]
        ]
    )


def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Back", callback_data="back")]
        ]
    )
