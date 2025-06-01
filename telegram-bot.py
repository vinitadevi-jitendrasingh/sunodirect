import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from murf import Murf
import tempfile
import requests

# Constants
API_KEY = "ap2_494cd5c1-262d-4d54-bfb0-8e8b7aede06d"
BOT_TOKEN = "7499405577:AAFsJLNZOfXJNWOIHnMXhDc-4KQYXox0Kl4"
DEFAULT_VOICE = "en-US-terrell"

# Initialize Murf client
murf_client = Murf(api_key=API_KEY)

# Start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to *SunoDirect!*")

# Help command
def help_command(update: Update, context: CallbackContext):
    help_text = """List of Commands:
/start - Welcome message
/help - Command list
/convert - Convert text to audio
/stop - Dummy stop command
"""
    update.message.reply_text(help_text)

# Convert command
def convert(update: Update, context: CallbackContext):
    if context.args:
        text = " ".join(context.args)
        try:
            update.message.reply_text("🔄 Converting text to speech...")
            res = murf_client.text_to_speech.generate(text=text, voice_id=DEFAULT_VOICE)
            audio_url = res.audio_file

            if not audio_url:
                update.message.reply_text("❌ Failed to generate audio.")
                return

            # Download and send
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                f.write(requests.get(audio_url).content)
                f_path = f.name

            update.message.reply_audio(audio=open(f_path, 'rb'))
            os.remove(f_path)

        except Exception as e:
            update.message.reply_text(f"❌ Error: {str(e)}")
    else:
        update.message.reply_text("❗ Please provide text. Example:\n/convert Hello world")

# Dummy stop command
def stop(update: Update, context: CallbackContext):
    update.message.reply_text("🛑 No playback to stop.")

# Main function
def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("convert", convert))
    dp.add_handler(CommandHandler("stop", stop))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
