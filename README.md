# Telegram Video Message Bot

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/downloads/)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-blue)](https://docs.aiogram.dev/)
[![Stars](https://img.shields.io/github/stars/bohd4nx/Telegram-Video-Bot)](https://github.com/bohd4nx/Telegram-Video-Bot/)

</div>

Convert regular videos into round video messages (video notes) that stand out in Telegram chats.

## ✨ Features

- 🎥 **Video to Video Note** - Convert any video to round video message format
- ⚡ **Fast Processing** - Optimized conversion with automatic resizing
- 📐 **Smart Cropping** - Automatic centering and aspect ratio handling
- 🔄 **User-Friendly** - Simple interface with inline keyboards
- 🛡️ **Error Handling** - Comprehensive error management and user feedback

## 🚀 Quick Start

1. **Clone and install**
   ```bash
   git clone https://github.com/bohd4nx/Telegram-Video-Bot.git
   cd Telegram-Video-Bot
   pip install -r requirements.txt
   ```

2. **Install FFmpeg**
   ```bash
   # Windows (chocolatey)
   choco install ffmpeg
   
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # macOS
   brew install ffmpeg
   ```

3. **Configure** - Fill `config.ini`:
   ```ini
   [Bot]
   BOT_TOKEN = your_bot_token_from_botfather
   ```

4. **Run**
   ```bash
   python main.py
   ```

### How to Use

| Action              | Description                           |
|---------------------|---------------------------------------|
| **Send Video**      | Upload any video file to convert      |
| **Get Video Note**  | Receive processed round video message |
| **Forward & Share** | Forward the video note to any chat    |

#### 📹 Video Processing

1. Start the bot with `/start`
2. Send any video file (MP4 recommended)
3. Wait for processing (15-30 seconds) - will be optimized later
4. Receive your round video message
5. Forward to any chat with "Hide sender's name" option

### 📝 Video Requirements

- **Format**: MP4 (recommended), other formats supported
- **Duration**: Maximum 60 seconds
- **Size**: Up to 20MB
- **Quality**: 480p recommended for faster processing
- **Aspect Ratio**: Square videos work best

### Output Specifications

- **Resolution**: 360x360 pixels (optimized for Telegram)
- **Format**: Round video note compatible with all Telegram clients
- **Audio**: Preserved from original video
- **Codec**: H.264 with AAC audio

## ⚙️ Technical Details

- **Async Processing**: Fully asynchronous video processing
- **MoviePy Integration**: Professional video editing capabilities
- **Temporary Files**: Secure handling with automatic cleanup
- **Error Recovery**: Handles file size limits and permission errors
- **Memory Efficient**: Optimized for server deployment

### Error Handling

- **File Too Large**: Automatic detection of 20MB+ files
- **Voice Messages Disabled**: Guides users to enable voice messages
- **Processing Errors**: Detailed error reporting and recovery

---

<div align="center">

#### Made with ❤️ by [@bohd4nx](https://t.me/bohd4nx)

**Star ⭐ this repo if you found it useful!**

</div>



