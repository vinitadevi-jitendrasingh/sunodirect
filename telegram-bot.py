import os
import tempfile
import requests
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from murf import Murf

API_KEY = "ap2_494cd5c1-262d-4d54-bfb0-8e8b7aede06d"
BOT_TOKEN = "7499405577:AAFsJLNZOfXJNWOIHnMXhDc-4KQYXox0Kl4"
DEFAULT_VOICE = "en-US-terrell"

user_settings = {}
murf_client = Murf(api_key=API_KEY)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to SunoDirect!")

def help_command(update: Update, context: CallbackContext):
    help_text = """*List of Commands*:
/start — Welcome
/help — All commands
/convert — Convert text to audio
/stop — Stop audio"""
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

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                audio_data = requests.get(audio_url).content
                f.write(audio_data)
                f_path = f.name

            update.message.reply_audio(audio=open(f_path, 'rb'))
            os.remove(f_path)
        except Exception as e:
            update.message.reply_text(f"❌ Error: {str(e)}")
    else:
        update.message.reply_text("❗ Example: SunoDirect")

def set_language(update: Update, context: CallbackContext):
    update.message.reply_text("🌐 Language change not supported directly. Use /voice instead.")

def set_voice(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if context.args:
        voice = context.args[0]
        if user_id not in user_settings:
            user_settings[user_id] = {}
        user_settings[user_id]["voice"] = voice
        update.message.reply_text(f"✅ Voice set to: {voice}")
    else:
        update.message.reply_text("❗ Example: /voice en-US-terrell")

def settings(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    prefs = user_settings.get(user_id, {"voice": DEFAULT_VOICE})
    update.message.reply_text(f"🔧 Settings:\nVoice: {prefs['voice']}")

def about(update: Update, context: CallbackContext):
    update.message.reply_text("🎵 SunoDirect uses Murf AI to convert text into realistic audio!")

def stop(update: Update, context: CallbackContext):
    update.message.reply_text("🛑 No active audio to stop, but thank you for using the bot!")

def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("convert", convert))
    dp.add_handler(CommandHandler("stop", stop))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
