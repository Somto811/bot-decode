import os
import json
import logging
import requests
from base64 import urlsafe_b64decode
from datetime import datetime
from urllib.parse import parse_qs, urlparse, unquote, quote
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from colorama import init, Fore, Style

# Setup colorama
init(autoreset=True)

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Define color codes
merah = Fore.LIGHTRED_EX
hijau = Fore.LIGHTGREEN_EX
putih = Fore.LIGHTWHITE_EX
kuning = Fore.LIGHTYELLOW_EX
line = putih + "~" * 50

# Define the Telegram bot token
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TOKEN:
    raise ValueError("Token bot tidak diset di variabel lingkungan.")

def percent_encode(data):
    """Encode specific characters for URL."""
    return quote(data, safe='')

def decode_url_data(url):
    try:
        # Parse URL and query params
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        fragment_params = parse_qs(parsed_url.fragment)

        # Get and decode tgWebAppData
        tg_web_app_data = fragment_params.get('tgWebAppData', [''])[0]
        decoded_data = unquote(tg_web_app_data)

        # Find the end of relevant data
        end_index = decoded_data.find('&tgWebApp')
        if end_index != -1:
            decoded_data = decoded_data[:end_index]

        # Decode and format data
        formatted_data = unquote(decoded_data)
        formatted_data = formatted_data.replace('&tgWebApp', ' ')

        # Convert to JSON if possible
        try:
            json_data = json.loads(formatted_data)
            formatted_data = json.dumps(json_data, indent=4)
        except json.JSONDecodeError:
            pass

        # Percent-encode the formatted data
        formatted_data = percent_encode(formatted_data)

        # Add query_id prefix
        return 'query_id=' + formatted_data
    except Exception as e:
        logger.error(f"Terjadi kesalahan saat mendecode URL: {e}")
        return 'Terjadi kesalahan saat memproses URL.'

async def handle_message(update: Update, context):
    message_text = update.message.text

    try:
        # Check if the message contains URL with 'tgWebAppData'
        if 'tgWebAppData=' in message_text:
            formatted_data = decode_url_data(message_text)
        else:
            # Decode the entire message
            decoded_message = unquote(message_text)
            formatted_data = decoded_message.replace('&tgWebApp', ' ')
            formatted_data = ' '.join(formatted_data.split())

            # Percent-encode the decoded message
            formatted_data = percent_encode(formatted_data)

            formatted_data = '```\n' + formatted_data + '\n```'.replace('\n', ' ')

        await update.message.reply_text(formatted_data, parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logger.error(f"Terjadi kesalahan saat memproses pesan: {e}")
        await update.message.reply_text('Terjadi kesalahan saat memproses pesan.')

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()
