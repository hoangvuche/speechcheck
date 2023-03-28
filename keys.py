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
        if isinstance(keyword, Keyword):
            self._keywords[keyword] = ''
        elif isinstance(keyword, list):
            for key in keyword:
                self._keywords[key] = ''

    def remove(self, keyword):
        if isinstance(keyword, Keyword):
            try:
                del self._keywords[keyword]
            except KeyError:
                print('Keyword {0} not existed'.format(keyword.text))
        elif isinstance(keyword, list):
            for key in keyword:
                try:
                    del self._keywords[key]
                except KeyError:
                    print('Keyword {0} not existed'.format(key.text))

    def refresh(self, view):
        view.refresh(self._keywords)


if __name__ == '__main__':
    key1 = Keyword('key 1')
    key2 = Keyword('key 2')
    keys = Keywords([key1, key2])
    for keyword in keys.keywords:
        print(keyword.text)

    key3 = Keyword('key 3')
    keys.append(key3)

    for keyword in keys.keywords:
        print(keyword.text)

    key4 = Keyword('key 4')
    otherkeys = [key3, key4]
    keys.append(otherkeys)

    for k in keys.keywords:
        print(k.text)

    keys.remove(key2)

    for k in keys.keywords:
        print(k.text)

    newkey = Keyword('sdfsdf')
    keys.remove([key4, key3])

    for k in keys.keywords:
        print(k.text)



