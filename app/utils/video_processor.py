import logging
import tempfile
from datetime import datetime
from pathlib import Path

import moviepy.config as mp_config
from aiogram.exceptions import TelegramEntityTooLarge, TelegramForbiddenError
from aiogram.types import Message, FSInputFile
from app.utils.texts import Messages
from moviepy import VideoFileClip

mp_config.LOGGER = logging.getLogger('moviepy')
mp_config.LOGGER.setLevel(logging.ERROR)

logger = logging.getLogger(__name__)


# TODO: Add a background when downloading a video (like in the original video message in Telegram), speed up processing
# One video processing takes about 15-30 seconds (i'll try to optimize it later)

async def process_video(message: Message):
    user_id = message.from_user.id
    current_time = datetime.now().strftime("%H-%M-%S-%f")

    processing_message = None
    try:
        file_id = message.video.file_id
        file = await message.bot.get_file(file_id)

        processing_message = await message.reply(Messages["processing"])

        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as input_tmp, \
                tempfile.NamedTemporaryFile(suffix='_output.mp4', delete=False) as output_tmp:

            input_file = Path(input_tmp.name)
            output_file = Path(output_tmp.name)

        await message.bot.download_file(file.file_path, input_file)

        with VideoFileClip(str(input_file), audio=True) as input_video:
            circle_size = 360
            aspect_ratio = input_video.w / input_video.h

            dimensions = {
                'landscape': {'width': int(circle_size * aspect_ratio), 'height': circle_size},
                'portrait': {'width': circle_size, 'height': int(circle_size / aspect_ratio)}
            }

            new_dimensions = dimensions['landscape' if input_video.w > input_video.h else 'portrait']

            resized_video = input_video.resized((new_dimensions['width'], new_dimensions['height']))
            output_video = resized_video.cropped(
                x_center=resized_video.w / 2,
                y_center=resized_video.h / 2,
                width=circle_size,
                height=circle_size
            )

            output_video.write_videofile(
                str(output_file),
                codec="libx264",
                audio_codec="aac",
                bitrate="5M",
                logger=None
            )
        video_note = FSInputFile(output_file, filename=f"{user_id}_{current_time}_output_video.mp4")

        await message.bot.send_video_note(
            chat_id=message.chat.id,
            video_note=video_note,
            duration=int(output_video.duration),
            length=circle_size
        )

        await processing_message.delete()

    except TelegramEntityTooLarge:
        logger.error(f"File too large for user {user_id}")
        await processing_message.edit_text(Messages["file_too_large"])
    except TelegramForbiddenError as e:
        if "VOICE_MESSAGES_FORBIDDEN" in str(e):
            logger.warning(f"Voice messages disabled for user {user_id}")
            await processing_message.edit_text(Messages["voice_messages_disabled"])
        else:
            logger.error(f"Forbidden error for user {user_id}: {str(e)}")
            await processing_message.edit_text(Messages["processing_error"].format(error=str(e)))
    except Exception as e:
        logger.error(f"Video processing error for user {user_id}: {str(e)}")
        await processing_message.edit_text(Messages["processing_error"].format(error=str(e)))
    finally:
        for file in [input_file, output_file]:
            try:
                file.exists() and file.unlink()
            except:
                pass
