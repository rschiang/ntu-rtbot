import os
import re
from datetime import datetime

'''
Base class for bot rules.
'''
class Rule(object):
    '''
    Check if a rule applies and `run()` the rule; return `None` otherwise.
    '''
    def match(self, bot, message):
        for expr in self.match_expr():
            m = re.search(expr, message.text)
            if m:
                return self.run(bot, message, **m.groupdict())
        return None

    '''
    Return a set of regular expression rules. In default implementation of
    `match()`, the returning value will be used to determine whether the rule
    applies, while extract `run()` arguments from named groups.
    '''
    def match_expr(self):
        raise NotImplementedError

    '''
    Executes the rule.
    '''
    def run(self, bot, message, **kwargs):
        pass


class HelloRule(Rule):
    def match_expr(self):
        return (r'(H(i|ello)|安安|[你妳]好|哈囉|嗨|阿屜|/start)',)

    def run(self, bot, message, **kwargs):
        return '嗨 {}，這裡是阿屜。'.format(message.from_user.username)

class FallbackRule(Rule):
    def match(self, bot, message):
        return self.run(bot, message)

    def run(self, bot, message, **kwargs):
        return '什麼什麼？你在說什麼？\n如果不知道要問些什麼，可以問我「你能幫上什麼忙？」'

class HelpRule(Rule):
    def match_expr(self):
        return (r'[你妳](能|可以|會).*(做|幹)(什麼|啥)',)

    def run(self, bot, message, **kwargs):
        return '你可以問我現在的時間、學校的天氣、或是會辦的狀況。'

class TimeRule(Rule):
    def match_expr(self):
        return (r'現在.*(時間|幾點|日期)', r'今天.*(幾[月號]|第幾天)')

    def run(self, bot, message, **kwargs):
        now = datetime.now()
        term = now.year - 1987
        days = (now - datetime(now.year if now.month > 7 else now.year + 1, 8, 1, 0, 0)).days + 1
        return '沒有問題，現在的時間是 {:%Y/%m/%d %H:%M}，也就是第 {} 屆的第 {} 天。'.format(now, term, days)

class WeatherRule(Rule):
    def match_expr(self):
        return (
            r'(天氣|氣象)',
            r'(公館|學校|[臺台][大北灣]|天龍國|大安).*(氣溫|溫度|下雨|太陽|多[熱冷])',
            r'(氣溫|濕度|雨量).*多[高底少多]',
        )

    def run(self, bot, message, **kwargs):
        import requests
        try:
            weather = requests.get('http://weather.ntustudents.org/api').json()
            return '現在學校的氣溫是 {temperature} 度，降雨強度 {rain} mm/h。'.format(**weather)
        except:
            return '暫時無法取得天氣資訊。'

class PhotoRule(Rule):
    IMAGE_DIR = os.environ.get('RT_IMAGE_DIR')

    def match_expr(self):
        return (r'會辦',)

    def run(self, bot, message, **kwargs):
        import glob
        from telegram import ChatAction

        recent_file = max(glob.iglob(IMAGE_DIR + '/*.jpg'), default=None)
        if recent_file:
            bot.sendChatAction(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
            with open(recent_file, 'rb') as f:
                caption = datetime.fromtimestamp(os.path.getctime(recent_file)).strftime('%Y/%m/%d %H:%M:%S')
                bot.sendPhoto(chat_id=chat_id, photo=f, caption=caption)
            return '這是會辦最近的情況。'
        
        return '目前沒有會辦最近的紀錄。'
