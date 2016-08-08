#!/usr/bin/env python3
import datetime
import os
from bottle import Bottle, request, abort
from telegram import Bot, Update

# Config
TELEGRAM_TOKEN = os.environ.get('RT_TELEGRAM_TOKEN')
WEBHOOK_TOKEN = os.environ.get('RT_WEBHOOK_TOKEN', 'RT')
BASE_URL = os.environ.get('RT_BASE_URL')
USERS = os.environ.get('RT_WHITELIST', '').split(',')

# Variables
app = Bottle()
bot = Bot(token=TELEGRAM_TOKEN)

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

    return {
        'method': 'sendMessage',
        'chat_id': chat_id,
        'text': '嗨 {}，這裡是阿屜。'.format(user.username),
    }

def set_webhook():
    return bot.set_webhook('{}/hooks/{}'.format(BASE_URL, WEBHOOK_TOKEN))

def generate_token():
    import base64
    return base64.urlsafe_b64encode(os.urandom(18)).decode()

if __name__ == '__main__':
    set_webhook()
    app.run()
