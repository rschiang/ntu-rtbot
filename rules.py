import re

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
    def match(self, bot, message):
        for keyword in ['/start', '安安', '你好', '哈囉', '嗨']:
            if keyword in message.text:
                return self.run(bot, message)
        return None

    def run(self, bot, message, **kwargs):
        return '嗨 {}，這裡是阿屜。'.format(message.from_user.username)

class FallbackRule(Rule):
    def match(self, bot, message):
        return self.run(bot, message)

    def run(self, bot, message, **kwargs):
        return '什麼什麼？你在說什麼？\n如果不知道要問些什麼，可以問我「你能幫上什麼忙？」'
