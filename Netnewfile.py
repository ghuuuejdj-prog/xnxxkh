import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

# ----------------- CONFIGURATION -----------------
BOT_TOKEN = "8912653417:AAFjXANFbKEYabM7w2tDC8UjeFcWxM4VfVM"
BOT_USERNAME = "Happydownloadmp3_bot"
ADMIN_LINK = "https://t.me/heipko80"
CHANNEL_LINK = "https://t.me/+jmALjZNVKXlmY2E1"
VIDEO_BOT_LINK = "http://t.me/Happydownload_bot"
START_IMAGE_URL = "https://i.supaimg.com/2c2963a3-a72b-47fd-ba30-ac78827d2091/ffe7fa66-75be-482e-899d-ed723f04b609.jpg"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

USER_URLS = {}

async def send_welcome_menu(chat_id, context, user_first_name):
    welcome_text = (
        f"✨🌸 សួស្តី {user_first_name} 🧸! 🌸✨\n\n"
        "សូមស្វាគមន៍មកកាន់ Music / MP3 Downloader Bot 🎵💖\n"
        "───────────────────\n"
        "📥 **របៀបទាញយកបទចម្រៀង/អូឌីយ៉ូ** 🎀៖\n"
        "១. ចម្លង (Copy) Link ពី YouTube, TikTok, Facebook... 🔗\n"
        "២. ផ្ញើ (Paste) Link នោះមកកាន់ទីនេះ 💌\n"
        "៣. ចុចប៊ូតុងដើម្បីទាញយកជា MP3 លឿនរហ័ស 🚀✨"
    )
    
    # បន្ថែមប៊ូតុង Channel និង Bot ទាញយកវីដេអូ
    keyboard = [
        [
            InlineKeyboardButton("📢 ចូលរួម Channel 💖", url=CHANNEL_LINK),
            InlineKeyboardButton("🤖 Bot ទាញយកវីដេអូ 🎬", url=VIDEO_BOT_LINK)
        ],
        [
            InlineKeyboardButton("💬 ទំនាក់ទំនង Admin 💌", url=ADMIN_LINK)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=START_IMAGE_URL, 
        caption=welcome_text, 
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await send_welcome_menu(update.effective_chat.id, context, user.first_name)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    user_id = update.effective_user.id
    
    if not (url.startswith("http://") or url.startswith("https://")):
        await update.message.reply_text("❌ 🥺 សូមផ្ញើ Link ឱ្យបានត្រឹមត្រូវណា (ឧទាហរណ៍៖ https://...)")
        return

    USER_URLS[user_id] = url

    keyboard = [
        [
            InlineKeyboardButton("🎵 ទាញយក Audio (MP3 ទំហំតូច) 💖", callback_data="dl_audio")
        ],
        [
            InlineKeyboardButton("📢 ចូលរួម Channel", url=CHANNEL_LINK),
            InlineKeyboardButton("🤖 Bot វីដេអូ", url=VIDEO_BOT_LINK)
        ],
        [
            InlineKeyboardButton("❌ បោះបង់ / ចាប់ផ្តើមថ្មី 🧸", callback_data="cancel_action")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👇 ✨ សូមចុចប៊ូតុងខាងក្រោមដើម្បីទាញយកជា MP3៖", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "cancel_action":
        if user_id in USER_URLS:
            del USER_URLS[user_id]
        await query.delete_message()
        await send_welcome_menu(query.message.chat_id, context, query.from_user.first_name)
        return

    url = USER_URLS.get(user_id)
    if not url:
        await query.edit_message_text("❌ 🥺 ផុតកំណត់រង់ចាំហើយ! សូមផ្ញើ Link ម្ដងទៀតណា។")
        return

    await query.edit_message_text("⏳ 🧸 កំពុងទាញយក និងបំលែងជា MP3 (ទំហំតូច-លឿន)... ✨")

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    # កំណត់ទំហំ File ឲ្យតូច (Bitrate 96k) និងទាញយកបានលឿនពី YouTube, TikTok, Facebook
    ydl_opts = {
        'format': 'worstvideo+bestaudio/worst/bestaudio/best',  # ជ្រើសរើស Audio ដើម្បីកុំឲ្យទំហំធំ
        'outtmpl': f'downloads/{user_id}_%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '96',  # កាត់បន្ថយមក 96kbps ដើម្បទទួលបាន MB តូច និងទាញយកលឿន
        }],
        'max_filesize': 100 * 1024 * 1024, # កម្រិតត្រឹម 100MB
        'noplaylist': True,
        'quiet': True,
    }

    try:
        loop = asyncio.get_event_loop()
        filename = await loop.run_in_executor(None, download_file_sync, ydl_opts, url)

        await query.edit_message_text("📤 ✨ កំពុងផ្ញើអូឌីយ៉ូទៅ Telegram... 🌸")
        
        caption_text = (
            "✅ 💖 បាន Download MP3 ដោយជោគជ័យហើយ! 🧸✨\n\n"
            f"🤖 ទាញយកតាមរយៈ៖ @{BOT_USERNAME}"
        )

        keyboard = [
            [
                InlineKeyboardButton("📢 ចូលរួម Channel 💖", url=CHANNEL_LINK),
                InlineKeyboardButton("🤖 Bot ទាញយកវីដេអូ 🎬", url=VIDEO_BOT_LINK)
            ],
            [
                InlineKeyboardButton("🔄 ទាញយកបទផ្សេងទៀត 🚀", callback_data="cancel_action")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        with open(filename, 'rb') as file:
            await context.bot.send_audio(
                chat_id=query.message.chat_id,
                audio=file,
                caption=caption_text,
                reply_markup=reply_markup
            )

        if os.path.exists(filename):
            os.remove(filename)
        await query.delete_message()

    except Exception as e:
        logging.error(f"Error downloading: {e}")
        await query.edit_message_text(
            "❌ 🥺 សុំទោសផង មិនអាចទាញយកជា MP3 បានទេ!\n"
            "💡 មូលហេតុអាចមកពី Link ខុស, ជាប់ Restriction ឬ Server ខ្វះ FFmpeg។"
        )

def download_file_sync(ydl_opts, url):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        return base + '.mp3'

def main():
    app = Application.builder().token(BOT_TOKEN).read_timeout(300).write_timeout(300).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot MP3 ត្រូវបានចាប់ផ្ដើមដំណើរការដោយរលូន...")
    app.run_polling()

if __name__ == '__main__':
    main()
