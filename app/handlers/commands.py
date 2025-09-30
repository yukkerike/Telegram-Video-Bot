from aiogram import types

from app.utils.texts import Messages


async def handle_unknown_input(message: types.Message):
    await message.delete()
    await message.answer(Messages["unknown_input"])


async def start_command(message: types.Message):
    user = message.from_user
    text = Messages["start"].format(name=user.first_name).strip()
    await message.answer(text)


async def help_command(message: types.Message):
    await message.delete()
    await message.answer(Messages["help"].strip())
