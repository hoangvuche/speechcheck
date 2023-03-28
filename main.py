import sqlite3
from os import path

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty

import speech_recognition as sr

from controller import *


def transcribe_audio():
    print('Checking TC recording')
    audio_file = path.join(path.dirname(path.realpath(__file__)), "speech2.wav")

    # use the audio file as the audio source
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)  # read the entire audio file

    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        print("Google Speech Recognition thinks you said " + r.recognize_google(audio, language='vi-VN'))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


class RootWidget(FloatLayout):

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)

    def refresh(self, keywords):
        self.grd_keywords.clear_widgets()
        self.grd_keywords.bind(minimum_height=self.grd_keywords.setter('height'))
        for keyword in keywords:
            keyitem = KeywordItem(text=keyword.text)
            self.grd_keywords.add_widget(keyitem)


class SpeechQCApp(App):

    def on_start(self):
        self.get_db_connection()
        self.keywords = Keywords()
        controller = QCController(self.keywords, self.root)
        controller.refresh_keywords()

    def get_db_connection(self):
        try:
            self.con = sqlite3.connect('qcdb.db')
        except sqlite3.Error as error:
            print('Error while connecting to sqlite')

    def close_db_connection(self):
        if self.con:
            self.con.close()
            print('DB connection closed')

    def on_stop(self):
        self.close_db_connection()


class KeywordItem(FloatLayout):
    text = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.img.bind(on_touch_up=self.cb_on_touch_up)

    def cb_on_touch_up(self, touch, value):
        if self.img.collide_point(*value.pos):
            print('touch keyword', self.text)


if __name__ == '__main__':
    SpeechQCApp().run()
