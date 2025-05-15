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

# Verify Token
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN in environment variables")

# Fix imports
sys.path.append(str(Path(__file__).parent.resolve()))
try:
    from utils.youtube_search import search_youtube
    from utils.youtube_downloader import download_video, download_audio
    from utils.helpers import format_duration, clean_filename
except ImportError as e:
    logging.error(f"Import failed: {e}")
    raise

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 YouTube Bot Ready!\n"
        "Send YouTube URL or search query"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if 'youtube.com/watch' in text or 'youtu.be/' in text:
        await handle_url(update, text)
    else:
        await handle_search(update, text)

async def handle_url(update: Update, url: str):
    try:
        video_info = download_video(url, only_info=True)
        keyboard = [
            [InlineKeyboardButton("🎥 Download Video", callback_data=f"video_{url}")],
            [InlineKeyboardButton("🎵 Download Audio", callback_data=f"audio_{url}")]
        ]
        await update.message.reply_photo(
            photo=video_info['thumbnail'],
            caption=f"📹 {video_info['title']}\n⏱ {format_duration(video_info['duration'])}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"URL handling error: {e}")
        await update.message.reply_text("❌ Failed to process URL")

async def handle_search(update: Update, query: str):
    try:
        results = search_youtube(query)
        if not results:
            await update.message.reply_text("🔍 No results found")
            return
            
        for result in results[:3]:  # Show top 3 results
            keyboard = [
                [InlineKeyboardButton("⬇️ Download", callback_data=f"video_{result['url']}")]
            ]
            await update.message.reply_photo(
                photo=result['thumbnail'],
                caption=f"🔍 {result['title']}\n⏱ {format_duration(result['duration'])}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except Exception as e:
        logger.error(f"Search error: {e}")
        await update.message.reply_text("❌ Search failed")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    url = data.split('_')[1]
    
    try:
        if data.startswith('video_'):
            await query.edit_message_caption(caption="⏳ Downloading video...")
            video_path = download_video(url)
            await query.message.reply_video(
                video=open(video_path, 'rb'),
                supports_streaming=True
            )
            os.remove(video_path)
        elif data.startswith('audio_'):
            await query.edit_message_caption(caption="⏳ Downloading audio...")
            audio_path = download_audio(url)
            await query.message.reply_audio(
                audio=open(audio_path, 'rb')
            )
            os.remove(audio_path)
    except Exception as e:
        logger.error(f"Download failed: {e}")
        await query.message.reply_text("❌ Download failed")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()

if __name__ == '__main__':
    main()