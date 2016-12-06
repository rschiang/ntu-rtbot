#!/usr/bin/env python3
import os
import rules
from bottle import Bottle, request, abort
from telegram import Bot, Update, ChatAction

# Config
TELEGRAM_TOKEN = os.environ.get('RT_TELEGRAM_TOKEN')
WEBHOOK_TOKEN = os.environ.get('RT_WEBHOOK_TOKEN', 'RT')
BASE_URL = os.environ.get('RT_BASE_URL')
USERS = os.environ.get('RT_WHITELIST', '').split(',')

# Variables
app = Bottle()
bot = Bot(token=TELEGRAM_TOKEN)
rules = [
    rules.WeatherRule(),
    rules.PhotoRule(),
    rules.TimeRule(),
    rules.HelpRule(),
    rules.TeachDialogRule(),
    rules.DialogRule(),
    rules.HelloRule(),
    rules.FallbackRule(),
]

@app.post('/hooks/<token>')
def telegram_hook(token):
    if token != WEBHOOK_TOKEN:
        abort(401, 'Unauthorized')

    update = Update.de_json(request.json)
    if update.callback_query:
        return process_callback(update.callback_query)
    elif update.message:
        return process_message(update.message)

def process_callback(callback_query):
    user = callback_query.from_user
    if user.username not in USERS:
        return

    bot.answerCallbackQuery(callback_query.id)
    for rule in rules:
        if rule.query_callback(bot, callback_query):
            break

def process_message(message):
    chat_id = message.chat.id
    user = message.from_user

    # Filter out users
    if user.username not in USERS:
        return {
            'method': 'sendMessage',
            'chat_id': chat_id,
            'text': '哈囉 {}，我是阿屜。'.format(user.first_name),
        }

    for rule in rules:
        text = rule.match(bot, message)
        if text:
            return {
                'method': 'sendMessage',
                'chat_id': chat_id,
                'text': text,
            }

def set_webhook():
    return bot.set_webhook('{}/hooks/{}'.format(BASE_URL, WEBHOOK_TOKEN))

def generate_token():
    import base64
    return base64.urlsafe_b64encode(os.urandom(18)).decode()

if __name__ == '__main__':
    set_webhook()
    app.run()
