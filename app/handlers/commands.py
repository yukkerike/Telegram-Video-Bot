from aiogram import types
from app.handlers.keyboards import get_start_keyboard, get_back_keyboard
from app.utils.texts import Messages


async def handle_unknown_input(message: types.Message):
    await message.delete()
    await message.answer(Messages["unknown_input"])


async def start_message(obj, is_callback=False):
    user = obj.from_user
    text = Messages["start"].format(name=user.first_name).strip()

    if is_callback:
        await obj.message.edit_text(text, reply_markup=get_start_keyboard())
        await obj.answer()
    else:
        await obj.answer(text, reply_markup=get_start_keyboard())


async def help_handler(message: types.Message) -> None:
    await message.delete()
    await message.answer(Messages["help"].strip())


async def help_callback(callback: types.CallbackQuery):
    await callback.message.edit_text(
        Messages["help"].strip(),
        reply_markup=get_back_keyboard()
    )
    await callback.answer()


async def back_callback(callback: types.CallbackQuery):
    await start_message(callback, is_callback=True)
