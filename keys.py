from kivy.app import App

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

    def append(self, keywords, view):
        for key in keywords:
            if key not in self._keywords:
                # key not existed
                # Save into dict of keys
                self._keywords[key] = ''

                # Save into db
                cursor = App.get_running_app().con.cursor()
                sql = 'INSERT INTO keywords(keyword) VALUES(?)'
                cursor.execute(sql, (key.text,))
                App.get_running_app().con.commit()
                print('Saved', key.text)

        # Notify view for update
        self.refresh(view)

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
        cursor = App.get_running_app().con.cursor()
        sql = 'SELECT * FROM keywords'
        cursor.execute(sql)
        keys = cursor.fetchall()
        keywords = []
        for key in keys:
            keywords.append(Keyword(key[0]))
        self.keywords = keywords

        # Notify view for update
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



