import os
import sys
from pathlib import Path
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

# ===== CRITICAL TOKEN VERIFICATION =====
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError("ERROR: No TELEGRAM_BOT_TOKEN found in environment variables. "
                    "Please set it in Render's environment settings.")

# Fix path issues for Render
current_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(current_dir))

# Import utils after path fix
from utils.youtube_search import search_youtube
from utils.youtube_downloader import download_video, download_audio
from utils.helpers import format_duration, clean_filename

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
    🎬 YouTube Video Downloader Bot 🎬
    
    Send me:
    - YouTube URL to download
    - Search query to find videos
    
    Commands:
    /start - Show this message
    /help - Get help
    /audio - Download audio (reply to URL)
    """
    await update.message.reply_text(welcome_text)

async def handle_youtube_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    try:
        video_info = download_video(url, only_info=True)
        
        keyboard = [
            [
                InlineKeyboardButton("🎥 Video", callback_data=f"video_{url}"),
                InlineKeyboardButton("🎵 Audio", callback_data=f"audio_{url}"),
            ]
        ]
        
        caption = (f"🎬 {video_info['title']}\n"
                  f"⏱️ {format_duration(video_info['duration'])}\n"
                  f"👤 {video_info['channel']}")
                  
        await update.message.reply_photo(
            photo=video_info['thumbnail'],
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Error processing URL")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    url = data.split('_', 1)[1]
    
    if data.startswith('video_'):
        await query.edit_message_caption(caption="⏳ Downloading video...")
        try:
            video_path = download_video(url)
            await query.message.reply_video(
                video=open(video_path, 'rb'),
                caption="✅ Download complete!",
                supports_streaming=True
            )
            os.remove(video_path)
        except Exception as e:
            logger.error(f"Video download failed: {e}")
            await query.message.reply_text("❌ Failed to download video")
    
    elif data.startswith('audio_'):
        await query.edit_message_caption(caption="⏳ Downloading audio...")
        try:
            audio_path = download_audio(url)
            await query.message.reply_audio(
                audio=open(audio_path, 'rb'),
                caption="✅ Audio download complete!"
            )
            os.remove(audio_path)
        except Exception as e:
            logger.error(f"Audio download failed: {e}")
            await query.message.reply_text("❌ Failed to download audio")

def main():
    try:
        logger.info("Starting bot application...")
        app = Application.builder().token(TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_youtube_url))
        app.add_handler(CallbackQueryHandler(button_callback))
        
        logger.info("Bot is now polling...")
        app.run_polling()
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        raise

if __name__ == '__main__':
    main()