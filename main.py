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

    def load_keywords(self):
        pass


class SpeechQCApp(App):
    pass


if __name__ == '__main__':
    SpeechQCApp().run()
