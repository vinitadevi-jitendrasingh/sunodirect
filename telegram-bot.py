import os
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from murf import Murf
import tempfile
import requests

# Constants
API_KEY = "ap2_494cd5c1-262d-4d54-bfb0-8e8b7aede06d"
BOT_TOKEN = "7499405577:AAFsJLNZOfXJNWOIHnMXhDc-4KQYXox0Kl4"
DEFAULT_VOICE = "en-US-terrell"

# Store user settings in memory (for now)
user_settings = {}

# Initialize Murf client
murf_client = Murf(api_key=API_KEY)

# Commands

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Welcome to SunoDirect Bot!\nUse /help to see available commands.",
        parse_mode='Markdown'
    )

def help_command(update: Update, context: CallbackContext):
    help_text = """🛠 SunoDirect Commands:

/start — Welcome message and bot introduction
/help — List of available commands and usage instructions
/convert <text> — Convert the given text into audio
/language <code> — Set your preferred language (e.g., hi, en)
/voice <name> — Choose voice type (e.g., en-US-terrell)
/settings — View or change your preferences
/about — Learn more about SunoDirect bot
/stop — Stop the current audio playback
"""
    update.message.reply_text(help_text, parse_mode='Markdown')

def convert(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_pref = user_settings.get(user_id, {})
    voice_id = user_pref.get("voice", DEFAULT_VOICE)

    if context.args:
        text = " ".join(context.args)
        try:
            res = murf_client.text_to_speech.generate(
                text=text,
                voice_id=voice_id,
            )
            audio_url = res.audio_file

            # Download audio to send
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                audio_data = requests.get(audio_url).content
                f.write(audio_data)
                f_path = f.name

            update.message.reply_audio(audio=open(f_path, 'rb'))
            os.remove(f_path)
        except Exception as e:
            update.message.reply_text(f"❌ Error: {str(e)}")
    else:
        update.message.reply_text("❗ Please provide text to convert. Example: /convert Hello world")

def set_language(update: Update, context: CallbackContext):
    update.message.reply_text("🌐 Language settings are not supported directly in Murf API, use /voice to change voices.")

def set_voice(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if context.args:
        voice = context.args[0]
        if user_id not in user_settings:
            user_settings[user_id] = {}
        user_settings[user_id]["voice"] = voice
        update.message.reply_text(f"✅ Voice set to: {voice}")
    else:
        update.message.reply_text("❗ Please specify a voice. Example: /voice en-US-terrell")

def settings(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    prefs = user_settings.get(user_id, {"voice": DEFAULT_VOICE})
    update.message.reply_text(f"🔧 Your current settings:\nVoice: {prefs['voice']}")

def about(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🎵 SunoDirect Bot converts your text to high-quality voice using Murf AI!\nCreated for seamless audio messaging.",
        parse_mode='Markdown'
    )

def stop(update: Update, context: CallbackContext):
    update.message.reply_text("🛑 There's no active audio playback to stop, but thanks for using SunoDirect!")

# Main

def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("convert", convert))
    dp.add_handler(CommandHandler("language", set_language))
    dp.add_handler(CommandHandler("voice", set_voice))
    dp.add_handler(CommandHandler("settings", settings))
    dp.add_handler(CommandHandler("about", about))
    dp.add_handler(CommandHandler("stop", stop))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
