import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from aiogram.exceptions import TelegramEntityTooLarge, TelegramForbiddenError
from aiogram.types import FSInputFile

from app.utils.texts import Messages

# TODO: Optimize video processing pipeline for a large number of concurrent users
# TODO: Speed up processing as much as possible (consider resizing, batching, async ffmpeg, GPU acceleration)
# TODO: Reduce memory footprint during frame processing
# TODO: Ensure FFmpeg and OpenCV calls are non-blocking wherever possible

async def process_video(message):
    user_id = message.from_user.id
    time_str = datetime.now().strftime("%H-%M-%S-%f")
    proc_msg = await message.reply(Messages["processing"])
    try:
        f = await message.bot.get_file(message.video.file_id)
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as in_f, \
                tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_f, \
                tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as out_f:
            in_path, tmp_path, out_path = Path(in_f.name), Path(tmp_f.name), Path(out_f.name)
        await message.bot.download_file(f.file_path, in_path)

        cap = cv2.VideoCapture(str(in_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        w, h = int(cap.get(3)), int(cap.get(4))

        scale = min(720 / max(w, h), 1.0)
        w_scaled, h_scaled = int(w * scale), int(h * scale)
        size = min(w_scaled, h_scaled, 640) - (min(w_scaled, h_scaled, 640) % 2)

        out = cv2.VideoWriter(str(tmp_path), cv2.VideoWriter.fourcc(*'mp4v'), fps, (size, size))
        mask = np.zeros((size, size), np.uint8)
        cv2.circle(mask, (size // 2, size // 2), size // 2, 255, -1)

        while True:
            ret, frame = cap.read()
            if not ret: break
            frame = cv2.resize(frame, (w_scaled, h_scaled))
            crop = frame[(h_scaled - size) // 2:(h_scaled + size) // 2, (w_scaled - size) // 2:(w_scaled + size) // 2]
            out.write(np.where(mask[:, :, None] == 255, crop, 255))
        cap.release()
        out.release()

        subprocess.run([
            "ffmpeg", "-y", "-i", str(tmp_path), "-i", str(in_path),
            "-c:v", "libx264", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0",
            "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            "-loglevel", "error", str(out_path)
        ], check=True)

        duration = int(total_frames / fps) if fps > 0 else None
        await message.bot.send_video_note(
            chat_id=message.chat.id,
            video_note=FSInputFile(out_path, filename=f"{user_id}_{time_str}_circle_video.mp4"),
            duration=duration,
            length=size
        )
        await proc_msg.delete()

    except TelegramEntityTooLarge:
        await proc_msg.edit_text(Messages["file_too_large"])
    except TelegramForbiddenError as e:
        if "VOICE_MESSAGES_FORBIDDEN" in str(e):
            await proc_msg.edit_text(Messages["voice_messages_disabled"])
        else:
            await proc_msg.edit_text(Messages["processing_error"].format(error=str(e)))
    except Exception as e:
        await proc_msg.edit_text(Messages["processing_error"].format(error=str(e)))
    finally:
        for f in [in_path, tmp_path, out_path]:
            if f.exists(): f.unlink()
