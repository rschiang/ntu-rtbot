import re

class RuleBase(object):

    def match(self, bot, message):
        for expr in self.match_exprs():
            m = re.search(expr, message.text)
            if m:
                return self.run(bot, message, **m.groupdict())
        return None

    def match_exprs(self):
        raise NotImplementedError

    def run(self, bot, message, **kwargs):
        pass
