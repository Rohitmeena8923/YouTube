import os
import sys
from pathlib import Path

# Add this to ensure Python can find your utils module
sys.path.append(str(Path(__file__).parent.resolve()))

# Now import your utils
from utils.youtube_search import search_youtube
from utils.youtube_downloader import download_video, download_audio
from utils.helpers import format_duration, clean_filename

# [Rest of your existing app.py code...]

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from environment variable
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the command /start is issued."""
    welcome_text = """
    🎬 *YouTube Video Downloader Bot* 🎬

    Send me:
    - A YouTube URL to download
    - A search query to find videos

    Commands:
    /start - Show this message
    /help - Get help
    /audio - Download audio only (reply to a YouTube URL)
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message when the command /help is issued."""
    help_text = """
    🔍 *How to use this bot:*

    1. *Download videos*:
       - Send a YouTube URL (e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ)
       - Or reply to a YouTube URL with /audio to download as MP3

    2. *Search videos*:
       - Just type what you're looking for (e.g., "latest tech news")
       - The bot will return top results

    3. *Audio only*:
       - Reply to a YouTube URL with /audio to get MP3

    ⚠️ Note: Large videos may take time to download.
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages - either YouTube URLs or search queries."""
    message = update.message.text

    # Check if it's a YouTube URL
    if 'youtube.com/watch' in message or 'youtu.be/' in message:
        await handle_youtube_url(update, context)
    else:
        await search_videos(update, context)

async def handle_youtube_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle YouTube URL by providing download options."""
    url = update.message.text
    try:
        # Get video info
        video_info = download_video(url, only_info=True)
        
        # Create keyboard with download options
        keyboard = [
            [
                InlineKeyboardButton("🎥 Video (720p)", callback_data=f"video_{url}"),
                InlineKeyboardButton("🎵 Audio Only", callback_data=f"audio_{url}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send video info with options
        caption = (
            f"🎬 *{video_info['title']}*\n"
            f"⏱️ Duration: {format_duration(video_info['duration'])}\n"
            f"👤 Channel: {video_info['channel']}\n"
            f"📊 Views: {video_info['view_count']:,}"
        )
        
        await update.message.reply_photo(
            photo=video_info['thumbnail'],
            caption=caption,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error processing YouTube URL: {e}")
        await update.message.reply_text("❌ Failed to process this YouTube URL. Please try another one.")

async def search_videos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search YouTube and return results."""
    query = update.message.text
    await update.message.reply_text(f"🔍 Searching YouTube for: {query}...")
    
    try:
        results = search_youtube(query)
        if not results:
            await update.message.reply_text("❌ No results found. Try a different query.")
            return
            
        for result in results[:5]:  # Limit to top 5 results
            keyboard = [
                [
                    InlineKeyboardButton("🎥 Download Video", callback_data=f"video_{result['url']}"),
                    InlineKeyboardButton("🎵 Download Audio", callback_data=f"audio_{result['url']}"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            caption = (
                f"🎬 *{result['title']}*\n"
                f"⏱️ Duration: {format_duration(result['duration'])}\n"
                f"👤 Channel: {result['channel']}"
            )
            
            await update.message.reply_photo(
                photo=result['thumbnail'],
                caption=caption,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Error searching YouTube: {e}")
        await update.message.reply_text("❌ Failed to search YouTube. Please try again later.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks for download options."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    url = data.split('_', 1)[1]
    
    if data.startswith('video_'):
        await query.edit_message_caption(caption=f"⏳ Downloading video... This may take a while for longer videos.")
        try:
            video_path = download_video(url)
            await query.message.reply_video(
                video=open(video_path, 'rb'),
                caption=f"✅ Here's your downloaded video!",
                supports_streaming=True
            )
            os.remove(video_path)  # Clean up
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            await query.message.reply_text("❌ Failed to download video. Please try again.")
    
    elif data.startswith('audio_'):
        await query.edit_message_caption(caption=f"⏳ Downloading audio... This may take a while for longer tracks.")
        try:
            audio_path = download_audio(url)
            await query.message.reply_audio(
                audio=open(audio_path, 'rb'),
                caption=f"✅ Here's your downloaded audio!"
            )
            os.remove(audio_path)  # Clean up
        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            await query.message.reply_text("❌ Failed to download audio. Please try again.")

async def audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /audio command when replying to a YouTube URL."""
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to a YouTube URL with this command.")
        return
    
    url = update.message.reply_to_message.text
    if 'youtube.com/watch' not in url and 'youtu.be/' not in url:
        await update.message.reply_text("The replied message is not a YouTube URL.")
        return
    
    await update.message.reply_text("⏳ Downloading audio... This may take a while for longer tracks.")
    try:
        audio_path = download_audio(url)
        await update.message.reply_audio(
            audio=open(audio_path, 'rb'),
            caption=f"✅ Here's your downloaded audio!"
        )
        os.remove(audio_path)  # Clean up
    except Exception as e:
        logger.error(f"Error downloading audio: {e}")
        await update.message.reply_text("❌ Failed to download audio. Please try again.")

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("audio", audio_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()