#!/usr/bin/env python3
import os
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

@app.post('/hooks/<token>')
def telegram_hook(token):
    if token != WEBHOOK_TOKEN:
        abort(401, 'Unauthorized')

    update = Update.de_json(request.json)
    chat_id = update.message.chat.id
    user = update.message.from_user
    response_dict = {
        'method': 'sendMessage',
        'chat_id': chat_id,
    }

    # Filter out users
    if user.username not in USERS:
        response_dict['text'] = '哈囉 {}，我是阿屜。'.format(user.first_name)
        return response_dict

    message = update.message.text
    if message == '/start' or '安安' in message:
        response_dict['text'] = '嗨 {}，這裡是阿屜。'.format(user.username)

    elif '天氣' in message:
        import requests
        try:
            weather = requests.get('http://weather.ntustudents.org/api').json()
            response_dict['text'] = '現在學校的氣溫是 {temperature} 度，降雨強度 {rain} mm/h。'.format(**weather)
        except:
            response_dict['text'] = '暫時無法取得天氣資訊。'

    elif '會辦' in message:
        import glob
        recent_file = max(glob.iglob(IMAGE_DIR + '/*.jpg'), default=None)
        if recent_file:
            bot.sendChatAction(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
            with open(recent_file, 'rb') as f:
                caption = datetime.fromtimestamp(os.path.getctime(recent_file)).strftime('%Y/%m/%d %H:%M:%S')
                bot.sendPhoto(chat_id=chat_id, photo=f, caption=caption)
            response_dict['text'] = '這是會辦最近的情況。'
        else:
            response_dict['text'] = '目前沒有會辦最近的紀錄。'

    elif '現在' in message or '時間' in message:
        now = datetime.now()
        term = now.year - 1987
        days = (now - datetime(now.year if now.month > 7 else now.year + 1, 8, 1, 0, 0)).days + 1
        response_dict['text'] = '沒有問題，現在的時間是 {:%Y/%m/%d %H:%M}，也就是第 {} 屆的第 {} 天。'.format(now, term, days)

    elif '你能' in message:
        response_dict['text'] = '你可以問我現在的時間、學校的天氣、或是會辦的狀況。'

    else:
        response_dict['text'] = '什麼什麼？你在說什麼？\n如果不知道要問些什麼，可以問我「你能幫上什麼忙？」'

    return response_dict

def set_webhook():
    return bot.set_webhook('{}/hooks/{}'.format(BASE_URL, WEBHOOK_TOKEN))

def generate_token():
    import base64
    return base64.urlsafe_b64encode(os.urandom(18)).decode()

if __name__ == '__main__':
    set_webhook()
    app.run()
