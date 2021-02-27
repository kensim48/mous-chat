#!/usr/bin/env python
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
"""

import logging
import requests
import json

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

RASA_CHATBOT_URL = 'http://192.168.1.50:5005/webhooks/rest/webhook'

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')



def chatbot(update: Update, context: CallbackContext) -> None:
    """chatbot the user message."""
    print(update.message.chat.id)
    payload= json.dumps({"sender": update.message.chat.id,"message": update.message.text})
    headers = {'Content-Type': 'application/json'}

    response = requests.request("POST", RASA_CHATBOT_URL, headers=headers, data=payload)
    print('INPUT: ', update.message.text)
    print(response.text)
    reply_list = json.loads(response.text)


    # pass back RASA chatbot response
    for reply in reply_list:
        if "text" in reply:
            update.message.reply_text(reply["text"])
        else:
            update.message.reply_text(reply["image"])
    

def connectUser(update: Update, context: CallbackContext) -> None:



def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("1652772350:AAH4J5QW9-aZZWZT2Qpf0OtcQRvXtVGcAGo")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on noncommand i.e message - chatbot the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, chatbot))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
