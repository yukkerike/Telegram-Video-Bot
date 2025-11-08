import math
import tempfile
from datetime import datetime
from pathlib import Path

import ffmpeg
from aiogram.exceptions import TelegramEntityTooLarge, TelegramForbiddenError
from aiogram.types import FSInputFile

from app.utils.texts import Messages

# TODO: Optimize video processing pipeline for a large number of concurrent users
# TODO: Speed up processing as much as possible (consider resizing, batching, async ffmpeg, GPU acceleration)
# TODO: Reduce memory footprint during frame processing
# TODO: Ensure FFmpeg calls are non-blocking wherever possible


async def process_video(message):
    user_id = message.from_user.id
    time_str = datetime.now().strftime("%H-%M-%S-%f")
    proc_msg = await message.reply(Messages["processing"])

    in_path = None
    segment_paths = []

    try:
        f = await message.bot.get_file(message.video.file_id)
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as in_f:
            in_path = Path(in_f.name)
        await message.bot.download_file(f.file_path, in_path)

        probe_input = ffmpeg.probe(str(in_path))
        total_duration = float(probe_input["format"]["duration"])
        num_segments = math.ceil(total_duration / 60)

        await proc_msg.edit_text(
            Messages["video_info"].format(
                duration=int(total_duration), segments=num_segments
            )
        )

        current_time = 0
        segment_num = 1

        while current_time < total_duration:
            segment_duration = min(60, total_duration - current_time)

            with tempfile.NamedTemporaryFile(
                suffix=".mp4", delete=False
            ) as out_f:
                output_path = Path(out_f.name)

            stream = ffmpeg.input(
                str(in_path),
                ss=current_time,
                t=segment_duration,
                hwaccel="auto",
            )

            (
                ffmpeg.output(
                    (
                        stream.video.filter(
                            "crop",
                            "min(in_w,in_h)",
                            "min(in_w,in_h)",
                            "(in_w-min(in_w,in_h))/2",
                            "(in_h-min(in_w,in_h))/2",
                        )
                        .filter("scale", 640, -1, flags="lanczos")
                        .filter("format", "yuva420p")
                        .filter(
                            "geq",
                            r="if(lt(hypot(X-W/2,Y-H/2),W/2),r(X,Y),255)",
                            g="if(lt(hypot(X-W/2,Y-H/2),W/2),g(X,Y),255)",
                            b="if(lt(hypot(X-W/2,Y-H/2),W/2),b(X,Y),255)",
                        )
                        .filter("format", "yuv420p")
                    ),
                    stream.audio,
                    str(output_path),
                    vcodec="libx264",
                    crf=25,
                    preset="ultrafast",
                    tune="fastdecode",
                    fpsmax=60,
                    acodec="aac",
                    audio_bitrate="96k",
                    format="mp4",
                    movflags="+faststart",
                    threads="0",
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )

            probe = ffmpeg.probe(str(output_path))
            actual_duration = int(float(probe["format"]["duration"]))
            segment_paths.append((output_path, actual_duration, 640))

            current_time += 60
            segment_num += 1

        for idx, (seg_path, duration, size) in enumerate(segment_paths, 1):
            await message.bot.send_video_note(
                chat_id=message.chat.id,
                video_note=FSInputFile(seg_path, filename=f"{user_id}_{time_str}_segment_{idx:03d}.mp4"),
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
        if in_path and in_path.exists():
            in_path.unlink()
        for seg_path, _, _ in segment_paths:
            if seg_path.exists():
                seg_path.unlink()
        if output_path and output_path.exists():
            output_path.unlink()
