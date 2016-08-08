import requests
from datetime import datetime
from .rule import Rule

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
        try:
            weather = requests.get('http://weather.ntustudents.org/api').json()
            return '現在學校的氣溫是 {temperature} 度，降雨強度 {rain} mm/h。'.format(**weather)
        except:
            return '暫時無法取得天氣資訊。'
