import logging

from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from app.core.config import config
from app.handlers.commands import (
    handle_unknown_input,
    start_command,
    help_command
)
from app.utils.video_processor import process_video

logging.getLogger('aiogram.dispatcher').setLevel(logging.INFO)


class TelegramBot:
    def __init__(self) -> None:
        self.bot = Bot(
            token=config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp = Dispatcher(storage=MemoryStorage())

    async def setup(self) -> None:
        await self._register_commands()
        self._register_handlers()

    async def start_polling(self) -> None:
        await self.dp.start_polling(self.bot)

    async def close(self) -> None:
        await self.bot.session.close()

    async def _register_commands(self) -> None:
        commands = [
            types.BotCommand(command="start", description="🚀 Start the app"),
            types.BotCommand(command="help", description="📖 Show help information")
        ]
        await self.bot.set_my_commands(commands)

    def _register_handlers(self) -> None:
        self.dp.message.register(start_command, Command("start"))
        self.dp.message.register(help_command, Command("help"))
        self.dp.message.register(process_video, F.video)
        self.dp.message.register(handle_unknown_input, ~F.video & ~Command("start") & ~Command("help"))
