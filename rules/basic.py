from .rule import Rule

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
