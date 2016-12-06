#!/usr/bin/env python3
import glob
import os
import sys
from datetime import datetime
from PIL import Image, ImageStat
from telegram import Bot, ChatAction

# Config
TELEGRAM_TOKEN = os.environ.get('RT_TELEGRAM_TOKEN')
IMAGE_DIR = os.environ.get('RT_IMAGE_DIR')
MASTERS = [int(i) for i in os.environ.get('RT_MASTERS', '').split(',')]

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

def compare_time(time_a, time_b):
    delta_seconds = time_a - time_b
    if delta_seconds > 600:
        if delta_seconds % 3600 < 180:
            for master in MASTERS:
                last_seen = datetime.fromtimestamp(time_b)
                the_message = '哈囉，這裡是阿屜。攝影機似乎有一陣子沒有反應了呢。最後一次記錄的時間是 %m/%d %H 點 %M 分。'.format(last_seen)
                bot.sendMessage(chat_id=master, text=the_message)
        sys.exit()  # Delta too long

def compare_files(file_a, file_b):
    med_a, rms_a, stdev_a = histogram(file_a)
    med_b, rms_b, stdev_b = histogram(file_b)
    if abs(rms_a - rms_b) > 20:
        bot.sendMessage(chat_id=master, )
        is_occupying = (rms_a > rms_b)
        the_file = (file_a if is_occupying else file_b)
        the_message = '哈囉，這裡是阿屜。會辦似乎變得{}一些了。'.format('明亮' if is_occupying else '暗')
        for master in MASTERS:
            bot.sendMessage(chat_id=master, text=the_message)
            send_photo(the_file, chat_id=master)
            bot.sendMessage(chat_id=master, text='附上最近的狀況，還請多注意囉。')

if __name__ == '__main__':
    now = datetime.now()
    pattern = IMAGE_DIR + now.strftime('/%Y-%m-%dT*.jpg')
    recent_files = sorted(glob.iglob(pattern), reverse=True)

    is_iterating = (len(sys.argv) > 1 and sys.argv[1] == 'backtrace')
    time_a, time_b = 0, now.timestamp()
    while len(recent_files) >= 2:
        file_a, file_b = recent_files[0], recent_files[1]
        time_a, time_b = time_b, os.path.getctime(file_a)
        compare_time(time_a, time_b)
        compare_files(file_a, file_b)
        del recent_files[0]
        if not is_iterating:
            break
