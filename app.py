#!/usr/bin/env python3
import os
import rules
from bottle import Bottle, request, abort
from datetime import datetime
from telegram import Bot, Update, ChatAction

# Config
TELEGRAM_TOKEN = os.environ.get('RT_TELEGRAM_TOKEN')
WEBHOOK_TOKEN = os.environ.get('RT_WEBHOOK_TOKEN', 'RT')
BASE_URL = os.environ.get('RT_BASE_URL')
USERS = os.environ.get('RT_WHITELIST', '').split(',')
IMAGE_DIR = os.environ.get('RT_IMAGE_DIR')

# Variables
app = Bottle()
bot = Bot(token=TELEGRAM_TOKEN)
rules = [
    rules.HelloRule(),
    rules.FallbackRule(),
]

@app.post('/hooks/<token>')
def telegram_hook(token):
    if token != WEBHOOK_TOKEN:
        abort(401, 'Unauthorized')

    update = Update.de_json(request.json)
    chat_id = update.message.chat.id
    user = update.message.from_user

    # Filter out users
    if user.username not in USERS:
        return {
            'method': 'sendMessage',
            'chat_id': chat_id,
            'text': '哈囉 {}，我是阿屜。'.format(user.first_name),
        }

    message = update.message.text
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
