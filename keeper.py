import glob
import os
import sys
from datetime import datetime
from PIL import Image, ImageStat
from telegram import Bot, ChatAction

# Config
TELEGRAM_TOKEN = os.environ.get('RT_TELEGRAM_TOKEN')
IMAGE_DIR = os.environ.get('RT_IMAGE_DIR')
MASTERS = os.environ.get('RT_MASTERS', '').split(',')

# Variables
bot = Bot(token=TELEGRAM_TOKEN)

def histogram(fp):
    with Image.open(fp) as image:
        image.draft(mode='L', size=(320, 320))
        stat = ImageStat.Stat(image)
        return (stat.median[0], stat.rms[0], stat.stddev[0])

def send_photo(fp, chat_id):
    bot.sendChatAction(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
    with open(fp, 'rb') as f:
        caption = datetime.fromtimestamp(os.path.getctime(fp)).strftime('%Y/%m/%d %H:%M:%S')
        bot.sendPhoto(chat_id=chat_id, photo=f, caption=caption)

if __name__ == '__main__':
    now = datetime.now()
    pattern = IMAGE_DIR + now.strftime('/%Y-%m-%dT*.jpg')
    recent_files = sorted(glob.iglob(pattern), reverse=True)

    if len(recent_files) < 2:
        sys.exit()  # It's the start of the day

    file_a, file_b = recent_files[0], recent_files[1]
    delta_seconds = os.path.getctime(file_a) - os.path.getctime(file_b)
    if delta_seconds > 750:
        if delta_seconds < 1500:
            for master in MASTERS:
                bot.sendMessage(chat_id=master, text='哈囉，這裡是阿屜。攝影機似乎有一陣子沒有反應了呢。')
        sys.exit()  # Delta too long

    med_a, rms_a, stdev_a = histogram(file_a)
    med_b, rms_b, stdev_b = histogram(file_b)
    if (rms_a - rms_b) > 20:
        for master in MASTERS:
            bot.sendMessage(chat_id=master, text='哈囉，這裡是阿屜。會辦似乎變明亮一些了。')
            send_photo(rms_a, chat_id=master)
    elif (rms_b - rms_a) > 20:
        for master in MASTERS:
            bot.sendMessage(chat_id=master, text='哈囉，這裡是阿屜。會辦似乎變得暗一些了，這是最近的狀況。')
            send_photo(rms_b, chat_id=master)
