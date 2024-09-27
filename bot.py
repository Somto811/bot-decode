import os
import json
import logging
from urllib.parse import parse_qs, urlparse, unquote
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, MessageHandler, filters
from colorama import init, Fore

# Setup colorama
init(autoreset=True)

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the Telegram bot token
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TOKEN:
    raise ValueError("Token bot tidak diset di variabel lingkungan.")

def decode_url_data(url):
    try:
        # Parse URL and query params
        parsed_url = urlparse(url)
        fragment_params = parse_qs(parsed_url.fragment)
        
        # Get and decode tgWebAppData
        tg_web_app_data = fragment_params.get('tgWebAppData', [''])[0]
        decoded_data = unquote(tg_web_app_data)

        # Find the end of relevant data
        end_index = decoded_data.find('&tgWebApp')
        if end_index != -1:
            decoded_data = decoded_data[:end_index]

        # Attempt to parse JSON data
        json_data = json.loads(decoded_data)
        return json.dumps(json_data, indent=4)
    except json.JSONDecodeError:
        logger.error("JSON decode error: invalid JSON format.")
        return json.dumps({"error": "Invalid JSON format."})
    except Exception as e:
        logger.error(f"Error decoding URL: {e}")
        return json.dumps({"error": "Error processing the URL."})

async def handle_message(update: Update, context):
    message_text = update.message.text
    logger.info(f"Received message: {message_text}")

    try:
        # Check if the message contains a URL with 'tgWebAppData'
        if 'tgWebAppData=' in message_text:
            formatted_data = decode_url_data(message_text)
        else:
            # Decode the entire message
            decoded_message = unquote(message_text)
            formatted_data = {"message": decoded_message.replace('&tgWebApp', ' ')}

        # Escape reserved characters in the response message
        formatted_response = json.dumps(formatted_data, indent=4).replace('{', '\\{').replace('}', '\\}')
        
        await update.message.reply_text(formatted_response, parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text(json.dumps({"error": "Error processing message."}))

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()
