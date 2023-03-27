import sqlite3
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout

import speech_recognition as sr
from os import path


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
        self.get_db_connection()
        self.load_keywords()

    def load_keywords(self):
        cursor = self.conn.cursor()
        sql = 'select * from keywords'
        cursor.execute(sql)
        record = cursor.fetchall()
        for row in record:
            print(row)
        cursor.close()

    def get_db_connection(self):
        try:
            self.conn = sqlite3.connect('qcdb.db')
        except sqlite3.Error as error:
            print('Error while connecting to sqlite')

    def close_db_connection(self):
        if self.conn:
            self.conn.close()
            print('DB connection closed')


class SpeechQCApp(App):
    pass


if __name__ == '__main__':
    SpeechQCApp().run()
