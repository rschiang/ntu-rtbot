import glob
import os
from datetime import datetime, timedelta
from telegram import ChatAction, InlineKeyboardButton, InlineKeyboardMarkup
from .rule import Rule

IMAGE_DIR = os.environ.get('RT_IMAGE_DIR')

class PhotoRule(Rule):
    def match_expr(self):
        return (r'會辦',)

    def run(self, bot, message, **kwargs):
        recent_file = max(glob.iglob(IMAGE_DIR + '/*.jpg'), default=None)
        if recent_file:
            send_photo(recent_file, bot=bot, chat_id=message.chat.id)
            return '這是會辦最近的情況。'
        return '目前沒有會辦最近的紀錄。'

    def query_callback(self, bot, callback_query):
        namespace, _, payload = callback_query.data.partition(':')
        if namespace != 'photo': return

        try:
            cursor_time = datetime.strptime(payload, '%Y-%m-%d %H:%M:%S').timestamp()
        except ValueError: return

        recent_files = sorted(glob.iglob(IMAGE_DIR + '/*.jpg'), reverse=True)
        for recent_file in recent_files:
            if os.path.getctime(recent_file) < cursor_time:
                send_photo(recent_file, bot=bot, chat_id=callback_query.chat.id)
                break

        return True

def format_payload(time):
    return 'photo:{:%Y-%m-%d %H:%M:%S}'.format(time)

def send_photo(fp, bot, chat_id):
    bot.sendChatAction(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
    with open(fp, 'rb') as f:
        photo_time = datetime.fromtimestamp(os.path.getctime(fp))
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton('≪ 更早', callback_data=format_payload(photo_time - timedelta(minutes=5))),
                InlineKeyboardButton('< 較早', callback_data=format_payload(photo_time)),
                InlineKeyboardButton('較晚 >', callback_data=format_payload(photo_time + timedelta(minutes=2))),
            ],
            [
                InlineKeyboardButton('更新', callback_data='photo:capture'),
            ],
        ])
        caption = photo_time.strftime('%Y/%m/%d %H:%M:%S')
        bot.sendPhoto(chat_id=chat_id, photo=f, caption=caption, reply_markup=keyboard)
