import glob
import os
from datetime import datetime
from telegram import ChatAction
from .rule import Rule

IMAGE_DIR = os.environ.get('RT_IMAGE_DIR')

class PhotoRule(Rule):
    def match_expr(self):
        return (r'會辦',)

    def run(self, bot, message, **kwargs):
        recent_file = max(glob.iglob(IMAGE_DIR + '/*.jpg'), default=None)
        if recent_file:
            bot.sendChatAction(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
            with open(recent_file, 'rb') as f:
                caption = datetime.fromtimestamp(os.path.getctime(recent_file)).strftime('%Y/%m/%d %H:%M:%S')
                bot.sendPhoto(chat_id=chat_id, photo=f, caption=caption)
            return '這是會辦最近的情況。'

        return '目前沒有會辦最近的紀錄。'
