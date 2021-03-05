#!/usr/bin/env python
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
"""
from dotenv import load_dotenv

import logging
import requests
import json
import random
import string
import os

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
RASA_CHATBOT_URL = os.getenv("RASA_CHATBOT_URL")

DEBUG_MODE = True

list_of_user_intents = {}

list_of_room_intents = {}

pair_details = {}

list_of_pairs = {}
pair_position = {}

last_hash = None

tik_tok_chat = True

BOT_CHAT, HUMAN_CHAT, FIRST_QNS, SECOND_QNS, THIRD_QNS, FOURTH_QNS = range(6)

def random_string():
    return ''.join(random.choice('0123456789ABCDEF') for i in range(16))

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    if DEBUG_MODE:
        update.message.reply_text('DEBUG MODE ON\nTo save on costs, bot replies may be slow')
    update.message.reply_text('Hi Mousie_Bot here, good day to you.')
    update.message.reply_text('How are you today?')

    return FIRST_QNS

def first_qn_function(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    sender_id = update.message.chat.id
    FIRST_QNS_INTENTS = ['mood_great', 'mood_unhappy', 'mood_soso', 'mood_angry', 'mood_suicidal']
    intent = determine_intent(get_chatbot_intent(text), FIRST_QNS_INTENTS, update)[0]
    print('first question', text)
    list_of_user_intents[sender_id] = [intent]
    update.message.reply_text('Mousie_Bot wonders what you did today?')
    
    return SECOND_QNS

def second_qn_function(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    sender_id = update.message.chat.id
    SECOND_QNS_INTENTS = ['mood_great', 'mood_unhappy', 'mood_soso', 'mood_angry', 'mood_suicidal']
    intent = determine_intent(get_chatbot_intent(text), SECOND_QNS_INTENTS, update)[0]
    # intent = determine_intent(get_chatbot_intent(text), FIRST_QNS_INTENTS)

    update.message.reply_text('Mousie_Bot wants to help you to find a friend! Tell me about your hobby~')

    
    return THIRD_QNS

def third_qn_function(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    sender_id = update.message.chat.id

    THIRD_QUESTION_INTENT = ['hobby_gaming', 'hobby_partying', 'hobby_reading', 'hobby_sports']
    intent = determine_intent(get_chatbot_intent(text), THIRD_QUESTION_INTENT, update)[0]
    list_of_user_intents[sender_id].append(intent)


    update.message.reply_text('Share Mousie_Bot interesting topics that you want to discuss!')
    
    
    return FOURTH_QNS

def fourth_qn_function(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    sender_id = update.message.chat.id

    FOURTH_QNS_INTENT = ['topic_sustainabilty', 'topic_hobby', 'topic_technology', 'topic_relationship']
    intent_list = determine_intent(get_chatbot_intent(text), FOURTH_QNS_INTENT, update)
    list_of_user_intents[sender_id].append(intent_list)
    
    update.message.reply_text('Mousie_Bot understands, I will soon match you with another Mousier. Please wait for a moment.')
    matchmake_user(sender_id)
    print(sender_id)
    return HUMAN_CHAT


def matchmake_user(sender_id):
    intent = list_of_user_intents[sender_id]
    last_hash = None
    for room_hash in list_of_room_intents:
        other_intent = list_of_room_intents[room_hash]
        if (other_intent[0] == "mood_soso" and intent[0] == "mood_soso") or (other_intent[0] == "mood_soso" and intent[0] == "mood_great") or (other_intent[0] == "mood_great" and intent[0] == "mood_soso") or (other_intent[0] == "mood_great" and intent[0] == "mood_great") or (other_intent[0] == "mood_great" and intent[0] == "mood_unhappy") or (other_intent[0] == "mood_unhappy" and intent[0] == "mood_great"):
            if other_intent[1] == intent[1]:
                last_hash = room_hash
            for topics in intent[2]:
                if topics in other_intent[2]:
                    last_hash = room_hash
    if last_hash is None:
            last_hash = random_string()
            list_of_pairs[last_hash] = [sender_id]
            pair_position[sender_id] = last_hash
            list_of_room_intents[last_hash] = intent
    else:
        list_of_pairs[last_hash].append(sender_id)
        pair_position[sender_id] = last_hash
        last_hash = None

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def get_chatbot_intent(text) -> dict:
    """get response from chatbot the user message."""
    payload= json.dumps({"text": text})
    headers = {'Content-Type': 'application/json'}

    response = requests.request("POST", RASA_CHATBOT_URL, headers=headers, data=payload)

    print(response.text)
    intentList = json.loads(response.text)['intent_ranking']

    # pass back RASA chatbot intent
    return intentList

def determine_intent(intentList, possibleIntents, update):
    intent_order = []
    for intent in intentList:
        if intent['name'] in possibleIntents:
            intent_order.append(intent['name'])
            print(intent_order)
    if DEBUG_MODE:
        update.message.reply_text(json.dumps(intent_order))
    return intent_order


def displayChatbotResponse(update: Update, context: CallbackContext, reply_list) -> None:
    for reply in reply_list:
        if "text" in reply:
            update.message.reply_text(reply["text"])
        else:
            update.message.reply_text(reply["image"])
    
def basic_chatbot(update: Update, context: CallbackContext) -> None:
    """chatbot the user message."""
    print(update.message.chat.id)
    payload= json.dumps({"sender": update.message.chat.id,"message": update.message.text})
    headers = {'Content-Type': 'application/json'}

    response = requests.request("POST", 'http://192.168.1.50:5005/webhooks/rest/webhook', headers=headers, data=payload)
    print('INPUT: ', update.message.text)
    print(response.text)
    reply_list = json.loads(response.text)
    # pass back RASA chatbot response
    for reply in reply_list:
        if "text" in reply:
            update.message.reply_text(reply["text"])
        else:
            update.message.reply_text(reply["image"])
    
    return HUMAN_CHAT
    

def connectUser(update: Update, context: CallbackContext) -> None:
    if update.message.chat.id in pair_position:
        actual_pair = list_of_pairs[pair_position[update.message.chat.id]]
        print(list_of_pairs)
        if len(actual_pair) == 2:
            other_user = actual_pair[0] if actual_pair[0]!=update.message.chat.id else actual_pair[1]
            print(list_of_pairs, other_user)
            context.bot.send_message(chat_id=other_user, text=update.message.text)
        else:
            update.message.reply_text("Yo wait")



def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TELEGRAM_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    conv_handler = ConversationHandler(
        # entry_points=[MessageHandler(Filters.text & ~Filters.command, fourth_qn_function)],
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST_QNS: [ MessageHandler(Filters.text & ~Filters.command, first_qn_function)],
            SECOND_QNS: [ MessageHandler(Filters.text & ~Filters.command, second_qn_function)],
            THIRD_QNS: [ MessageHandler(Filters.text & ~Filters.command, third_qn_function)],
            FOURTH_QNS: [ MessageHandler(Filters.text & ~Filters.command, fourth_qn_function)],
            HUMAN_CHAT: [ MessageHandler(Filters.text & ~Filters.command, connectUser)]
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
