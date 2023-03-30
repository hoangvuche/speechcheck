import sqlite3
from os import path

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty
from kivy.utils import get_color_from_hex

import speech_recognition as sr

from controller import *
from newwidgets import *


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

    def bind_all(self):
        self.btn_add.bind(on_press=self.cb_on_add_press)

    def cb_on_add_press(self, instance):
        pnl = MessagePanel(size_hint=(None, None),
                           width=self.width * .5,
                           height=dp(44) * 3,
                           radius=[common.rounded_radius, common.rounded_radius,
                                   common.rounded_radius, common.rounded_radius])
        self.txt_keyword = TextInput(size_hint=(1, None), height=dp(44),
                                pos_hint={'center_x': .5, 'y': dp(68) / pnl.height},
                                hint_text='Nhập một keyword hoặc nhiều keyword cách bằng dấu phẩy')

        btnSave = Button(text='Lưu')
        btnSaveClose = Button(text='Lưu và thoát')
        btnClose = Button(text='Thoát')

        btnSave.bind(on_press=self.cb_on_save_press)
        btnSaveClose.bind(on_press=self.cb_on_save_close_press)
        btnClose.bind(on_press=self.cb_on_close_press)

        pnl_btn = GridLayout(cols=3, size_hint=(1, None), height=dp(44),
                             pos_hint={'x': 0, 'y':  dp(12) / pnl.height})
        pnl_btn.add_widget(btnSave)
        pnl_btn.add_widget(btnSaveClose)
        pnl_btn.add_widget(btnClose)

        pnl.add_widget(self.txt_keyword)
        pnl.add_widget(pnl_btn)

        self.popup_new_keyword = PopupWindow(pnl, use_buttons=False)
        self.popup_new_keyword.open()

    def cb_on_save_press(self, instance):
        self.save_keywords()

    def cb_on_save_close_press(self, instance):
        self.save_keywords()
        self.popup_new_keyword.dismiss()

    def save_keywords(self):
        keys = self.txt_keyword.text.strip().split(',')
        keywords = []
        for key in keys:
            keywords.append(Keyword(key.strip()))

        App.get_running_app().controller.save_keywords(keywords)
    def cb_on_close_press(self, instance):
        self.popup_new_keyword.dismiss()

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
        self.controller = QCController(self.keywords, self.root)
        self.controller.refresh_keywords()
        self.root.bind_all()

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
            btnEdit = RoundedButton(text='Sửa',
                                    size_hint=(None, None),
                                    width=dp(200), height=dp(44),
                                    radius=[(common.rounded_radius, common.rounded_radius),
                                            (common.rounded_radius, common.rounded_radius),
                                            (0, 0), (0, 0)],
                                    font_size='15sp',
                                    halign='left',
                                    padding_x=common.element_sep * 2,
                                    color=get_color_from_hex('#000000'),
                                    background_color_display=get_color_from_hex('#f3f4f5'))
            btnRemove = RoundedButton(text='Xóa',
                                    size_hint=(None, None),
                                    width=dp(200), height=dp(44),
                                    radius=[(0, 0), (0, 0),
                                            (common.rounded_radius, common.rounded_radius),
                                            (common.rounded_radius, common.rounded_radius)],
                                    font_size='15sp',
                                    halign='left',
                                    padding_x=common.element_sep * 2,
                                    color=get_color_from_hex('#000000'),
                                    background_color_display=get_color_from_hex('#f3f4f5'))

            btnEdit.bind(on_touch_up=self.cb_on_edit_touch_up)
            btnRemove.bind(on_touch_up=self.cb_on_remove_touch_up)

            pop_content = PopupMenuContent()
            pop_content.add_menu_item(btnEdit)
            pop_content.add_menu_item(HorizontalSeparator(height=dp(1)))
            pop_content.add_menu_item(btnRemove)

            pop_menu = PopMenu(value, pop_content)
            pop_menu.open()

    def cb_on_edit_touch_up(self, instance, value):
        if not instance.collide_point(*value.pos):
            return

        print(instance.text, self.text)

    def cb_on_remove_touch_up(self, instance, value):
        if not instance.collide_point(*value.pos):
            return

        print(instance.text, self.text)


if __name__ == '__main__':
    SpeechQCApp().run()
