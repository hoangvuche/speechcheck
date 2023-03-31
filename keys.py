import sqlite3
import re

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
            if not self.is_duplicate(key):
                # Only process if key is not already existed
                # Save into dict of keys
                self._keywords[key] = ''

                # Save into db
                cursor = App.get_running_app().con.cursor()
                sql = 'INSERT INTO keywords(keyword) VALUES(?)'
                try:
                    cursor.execute(sql, (key.text,))
                except sqlite3.IntegrityError:
                    print('Duplicate keyword', key.text)
                    continue
                App.get_running_app().con.commit()
                print('Saved', key.text)

        # Notify view for update
        self.refresh(view)

    def update(self, old_keyword, new_keyword, view):
        cursor = App.get_running_app().con.cursor()
        sql = 'UPDATE keywords SET keyword = ? WHERE keyword = ?'
        try:
            cursor.execute(sql, (new_keyword.text, old_keyword.text))
        except sqlite3.IntegrityError:
            print('Duplicate keyword', new_keyword.text)
        App.get_running_app().con.commit()
        print('Updated', old_keyword.text, 'to', new_keyword.text)
        self.refresh(view)

    def is_duplicate(self, keyword):
        for key in self.keywords:
            if key.text == keyword.text:
                return True
        return False

    def remove(self, keyword, view):
        cursor = App.get_running_app().con.cursor()
        sql = 'DELETE FROM keywords WHERE keyword = ?'
        cursor.execute(sql, (keyword.text,))
        App.get_running_app().con.commit()
        print('Removed keyword', keyword.text)
        self.refresh(view)

    def remove_all(self, view):
        cursor = App.get_running_app().con.cursor()
        sql = 'DELETE FROM keywords'
        cursor.execute(sql)
        App.get_running_app().con.commit()
        self.refresh(view)

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

    def check_keywords(self, transcript, view):
        # Check keywords
        result = {}
        result['transcript'] = transcript
        result['keywords'] = {}
        for keyword in self._keywords:
            # Check keyword existence one by one
            result['keywords'][keyword] = [m.start() for m in re.finditer(keyword.text, transcript)]

        # Mark found keywords
        for keyword, val in result['keywords'].items():
            result['transcript'] = self.check_keyword(keyword, val, result['transcript'])

        # Update UI
        view.display_keywordQC_result(result)

    def check_keyword(self, keyword, positions, transcript):
        accumulated_spaces = 0
        for pos in positions:
            transcript = (transcript[:pos + accumulated_spaces] + '[color=#ff0000][b]' + transcript[pos + accumulated_spaces:])
            accumulated_spaces += len('[color=#ff0000][b]')
            transcript = (transcript[:pos + len(keyword.text) + accumulated_spaces]
                          + '[/b][/color]' + transcript[pos + len(keyword.text) + accumulated_spaces:])
            accumulated_spaces += len('[/b][/color]')
        return transcript


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



