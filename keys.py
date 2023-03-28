class Keyword:

    def __init__(self, text=''):
        self._text = text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, val):
        self._text = val


class Keywords:

    def __init__(self, keywords=[]):
        self._keywords = {key: '' for key in keywords}

    @property
    def keywords(self):
        return self._keywords.keys()

    @keywords.setter
    def keywords(self, val):
        self._keywords = {item: '' for item in val}

    def append(self, keyword):
        self._keywords[keyword] = ''

    def remove(self, keyword):
        try:
            del self._keywords[keyword]
        except KeyError:
            print('Keyword {0} not existed'.format(keyword.text))

