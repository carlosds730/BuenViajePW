__author__ = 'Roly'

import feedparser


def check(list_1, list_2):
    for element in list_1:
        if element not in list_2:
            return False
    return True


def clean_result(_list):
    res = []
    for x in _list:
        tmp = ''
        _bool = True
        for word in x[1]:
            if word == '<':
                _bool = False
            if _bool:
                tmp += word
            if word == '>':
                _bool = True
        res.append((x[0], tmp, x[2], x[3]))
    return res


class WrapperRSS():
    def __init__(self, url):
        self.url = url
        self.feed = feedparser.parse(url)

    def get_news(self, key_words=[], total=-1):
        if total == -1:
            total = len(self.feed.entries)
        key_words = [z.lower() for z in key_words]
        count = 0
        result = []
        for x in self.feed.entries:
            if count < total:
                if not len(key_words):
                    try:
                        result.append((x.title, x.content[0]['value'], x.link, x.published))
                    except AttributeError:
                        result.append((x.title, x.description, x.link, x.published))
                    count += 1
                    continue
                categories = [y['term'].lower() for y in x.tags]
                if check(key_words, categories):
                    try:
                        result.append((x.title, x.content[0]['value'], x.link, x.published))
                    except AttributeError:
                        result.append((x.title, x.description, x.link, x.published))
                    count += 1
        return sorted(clean_result(result), key=lambda k: k[3])


if __name__ == '__main__':
    w = WrapperRSS(r'F:\\Work\\django-newsletter\\the_pr\\newsletter\\download.xml')
    for x in w.get_news():
        print
        print x[0]
        print x[1]
        print x[2]
        print x[3]
