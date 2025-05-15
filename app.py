import os
import os
import sys
from pathlib import Path
import logging

# CRITICAL PATH FIX - Add before any other imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

# Relative imports AFTER path modification
from utils.youtube_search import search_youtube
from utils.youtube_downloader import download_video, download_audio
from utils.helpers import format_duration, clean_filename

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

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

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_youtube_url))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    app.run_polling()

if __name__ == '__main__':
    main()