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
import random
import string

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

RASA_CHATBOT_URL = 'http://192.168.1.50:5005/webhooks/rest/webhook'

list_of_pairs = {}
pair_position = {}

last_hash = None

tik_tok_chat = True

BOT_CHAT, HUMAN_CHAT = range(2)
FIRST_QNS, SECOND_QNS, THIRD_QNS =  = map(chr, range(4))

def random_string():
    return ''.join(random.choice('0123456789ABCDEF') for i in range(16))

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi Mousie_Bot here, good day to you.')
    update.message.reply_text('How are you today?')

    return BOT_CHAT

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
    context.bot.send_message(chat_id=36160781, text=update.message.text)
    # pass back RASA chatbot response
    for reply in reply_list:
        if "text" in reply:
            update.message.reply_text(reply["text"])
        else:
            update.message.reply_text(reply["image"])
    
    return HUMAN_CHAT
    

def connectUser(update: Update, context: CallbackContext) -> None:
    global last_hash
    if update.message.chat.id in pair_position:
        actual_pair = list_of_pairs[pair_position[update.message.chat.id]]
        print(actual_pair)
        if len(actual_pair) == 2:
            other_user = actual_pair[0] if actual_pair[0]!=update.message.chat.id else actual_pair[1]
            print(list_of_pairs, other_user)
            context.bot.send_message(chat_id=other_user, text=update.message.text)
        else:
            update.message.reply_text("Yo wait")
    else:
        print(last_hash)
        if last_hash is None:
            last_hash = random_string()
            list_of_pairs[last_hash] = [update.message.chat.id]
            pair_position[update.message.chat.id] = last_hash
            print(last_hash)
        else:
            list_of_pairs[last_hash].append(update.message.chat.id)
            pair_position[update.message.chat.id] = last_hash
            last_hash = None



def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("1652772350:AAH4J5QW9-aZZWZT2Qpf0OtcQRvXtVGcAGo")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    conv_handler = ConversationHandler(
        # entry_points=[MessageHandler(Filters.text & ~Filters.command, connectUser)],
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST_QNS: [ MessageHandler(Filters.text & ~Filters.command, firstQns)]
            BOT_CHAT: [
                MessageHandler(Filters.text & ~Filters.command, chatbot)
            ],
            HUMAN_CHAT: [
                MessageHandler(Filters.text & ~Filters.command, connectUser)
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('start'), start)],
    )


    # on noncommand i.e message - chatbot the message on Telegram
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
