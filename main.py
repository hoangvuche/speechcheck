import os
import sys
if sys.__stdout__ is None or sys.__stderr__ is None:
    os.environ['KIVY_NO_CONSOLELOG'] = '1'

from threading import Thread

from kivy.uix.popup import Popup

from controller import *
from newwidgets import *
from activation import *


class RootWidget(FloatLayout):
    qc_result = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)

    def bind_all(self):
        self.btn_add.bind(on_touch_up=self.cb_on_add_up)
        self.btn_remove_all.bind(on_touch_up=self.cb_on_remove_all_up)
        self.btn_audio.bind(on_touch_up=self.cb_on_audio_up)
        self.btn_check.bind(on_touch_up=self.cb_on_check_up)
        self.btn_export.bind(on_touch_up=self.cb_on_export_up)

    def cb_on_export_up(self, instance, value):
        if not instance.collide_point(*value.pos):
            return

        if not hasattr(self, 'qc_result') or not self.qc_result:
            return

        self.qc_result['filename'] = os.path.split(self.lbl_file.text)

        result = App.get_running_app().controller.export_report(self.qc_result)
        if result:
            PopupMessage(message='Đã xuất ra {0}'.format(result)).open(animated=False)
        else:
            PopupMessage(message='Có lỗi xuất báo cáo').open(animated=False)

    def cb_on_add_up(self, instance, value):
        if not instance.collide_point(*value.pos):
            return
        self.show_add_keyword()

    def cb_on_remove_all_up(self, instance, value):
        if not instance.collide_point(*value.pos):
            return
        App.get_running_app().controller.remove_all()

    def cb_on_audio_up(self, instance, value):
        if not instance.collide_point(*value.pos) or instance.disabled:
            return
        self.show_media()

    def cb_on_check_up(self, instance, value):
        if not instance.collide_point(*value.pos) or instance.disabled:
            return
        if self.lbl_files.text == '':
            print('No files selected')
            return
        if hasattr(self, 'thread_transcription') and self.thread_transcription.is_alive():
            print('Another thread is running, please wait!')
            return

        instance.disabled = True
        self.btn_audio.disabled = True

        self.qc_result = []

        self.img_load.size = (dp(48), dp(48))
        self.pnl_result.clear_widgets()

        self.thread_transcription = Thread(target=App.get_running_app().controller.transcribe_audios,
                                           name='thread_transcription',
                                           args=(self.record_files,))
        self.thread_transcription.start()

    def show_add_keyword(self, keyword=None):
        self.add_key_content = AddNewKeywordPanel(width=self.width * .5, height=dp(44) * 3,
                                                  text=keyword.text if keyword else '',
                                                  keyword=keyword)
        self.add_key_content.btn_save.bind(on_press=self.cb_on_save_press)
        self.add_key_content.btn_save_close.bind(on_press=self.cb_on_save_close_press)
        self.add_key_content.btn_close.bind(on_press=self.cb_on_close_press)

        self.popup_dialog = PopupWindow(self.add_key_content, use_buttons=False)

        self.popup_dialog.open(animated=False)

    def show_activation(self):
        self.activation_content = ActivationDialog(width=self.width * .5, height=dp(44) * 3)
        self.activation_content.btn_save.bind(on_press=self.on_activation_save_press)
        self.activation_content.btn_close.bind(on_press=self.on_activation_close_press)

        self.popup_dialog = PopupWindow(self.activation_content, use_buttons=False)

        self.popup_dialog.open(animated=False)

    def on_size(self, instance, value):
        if hasattr(self, 'add_key_content'):
            self.add_key_content.width = self.width * .5

    def cb_on_save_press(self, instance):
        self.save_keywords()
        self.add_key_content.txt_keyword.text = ''

    def on_activation_save_press(self, instance):
        contact = self.activation_content.txt_keyword.text.strip()
        if len(contact) == 0:
            return

        if instance.text == 'Tiếp tục':
            # Send info to admin
            App.get_running_app().controller.validate_info(contact)
        else:
            # Verify activation key
            App.get_running_app().controller.verify_credential(self.activation_content.txt_keyword.text)

    def after_validate_info(self, success):
        if success:
            # Adjust screen accordingly
            self.activation_content.txt_keyword.text = ''
            self.activation_content.txt_keyword.hint_text = 'Hỏi quản lý để lấy key kích hoạt'
            self.activation_content.btn_save.text = 'Kích hoạt'

    def on_activation_close_press(self, instance):
        App.get_running_app().stop()

    def process_credential(self, activated):
        if activated:
            self.popup_dialog.dismiss()
        else:
            self.activation_content.txt_keyword.text = ''
            self.activation_content.txt_keyword.hint_text = 'Nhập email hoặc số điện thoại để kích hoạt'
            self.activation_content.btn_save.text = 'Tiếp tục'

    def cb_on_save_close_press(self, instance):
        self.save_keywords()
        self.popup_dialog.dismiss()

    def save_keywords(self, mode='add'):
        if self.add_key_content.txt_keyword.text.strip() == '':
            # Return if empty string
            return

        if self.add_key_content.keyword:
            # Edit
            keys = self.add_key_content.txt_keyword.text.strip()
        else:
            # Add
            keys = self.add_key_content.txt_keyword.text.strip().split(',')
        keywords = []

        if hasattr(self.add_key_content, 'old_keyword'):
            # Edit
            print('edit', self.add_key_content.old_keyword, self.add_key_content.old_keyword.text)
            App.get_running_app().controller.update_keyword(self.add_key_content.old_keyword, Keyword(text=keys))
        else:
            # Add
            for key in keys:
                keywords.append(Keyword(key.strip()))
            App.get_running_app().controller.save_keywords(keywords)

    def cb_on_close_press(self, instance):
        self.popup_dialog.dismiss()

    def refresh(self, keywords):
        self.grd_keywords.clear_widgets()
        self.grd_keywords.bind(minimum_height=self.grd_keywords.setter('height'))
        for keyword in keywords:
            keyitem = KeywordItem(text=keyword.text)
            self.grd_keywords.add_widget(keyitem)

    def activate(self, is_activated):
        if not is_activated:
            self.show_activation()

    def show_media(self):
        content = LoadDialog(load=self.load_media_file, cancel=self.dismiss_popup)
        self._popup = Popup(title="Chọn media", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load_media_file(self, path, filename):
        # Save selected file in a variable
        self.record_files = filename

        if App.get_running_app().mode == 'production':
            # Production mode
            # self.lbl_file.text = filename[0]
            self.lbl_files.text = '\n'.join(filename)
        else:
            # Debug mode
            # self.lbl_file.text = os.path.join('.', 'sample records', 'speech1.wav')
            self.lbl_files.text = '\n'.join((os.path.join('.', 'sample records', 'speech1.wav'),
                                            os.path.join('.', 'sample records', 'test.wav')))

        # Check audio file or otherwise
        for f in filename:
            audio_type = common.is_valid_audio(f)

            if not audio_type:
                PopupMessage(message=f'{f} không phải file Audio').open(animated=False)
                print(f'Invalid audio file: {f}')
                self.lbl_files.text = ''
                return
            else:
                # Audio file, start thread load audio
                print(f'Valid audio file: {f}')

        self.dismiss_popup()

    def dismiss_popup(self):
        self._popup.dismiss()

    def display_keyword_qc_result(self, result):
        self.img_load.size = (0, 0)                 # Hide loading image
        self.btn_check.disabled = False             # Enable button check record
        self.btn_audio.disabled = False             # Enable button audio selection
        self.qc_result.append(result)                       # Store result to a list
        Clock.schedule_once(self.draw_qc_result, -1)        # Draw statistics

    def draw_qc_result(self, value):
        self.pnl_result.add_widget(Label(text=self.qc_result[-1]['filename']))


class SpeechCheckResult(FloatLayout):
    pass


class SpeechQCApp(App):
    mode = 'debug'
    # mode = 'production'
    icon = os.path.join(common.get_bundle_dir(), 'images', 'anydo_104098.png')
    title = 'Record QC'

    def on_start(self):
        self.get_db_connection()
        self.activation = Activation()
        self.keywords = Keywords()
        self.controller = QCController(self.activation, self.keywords, self.root)
        self.controller.check_activation()
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
            btnEdit = RoundedImageButton(text='Sửa',
                                         source=os.path.join(common.get_bundle_dir(), 'images', 'edit.png'),
                                         icon_pos_hint='left',
                                         size_hint=(None, None),
                                         width=dp(200), height=dp(44),
                                         radius=[(common.rounded_radius, common.rounded_radius),
                                                 (common.rounded_radius, common.rounded_radius),
                                                 (0, 0), (0, 0)],
                                         font_size='15sp',
                                         halign='center',
                                         padding_x=common.element_sep * 2,
                                         color=get_color_from_hex('#000000'),
                                         background_color_display=get_color_from_hex('#f3f4f5'))
            btnRemove = RoundedImageButton(text='Xóa',
                                           source=os.path.join(common.get_bundle_dir(), 'images', 'remove.png'),
                                           icon_pos_hint='left',
                                           size_hint=(None, None),
                                           width=dp(200), height=dp(44),
                                           radius=[(0, 0), (0, 0),
                                                   (common.rounded_radius, common.rounded_radius),
                                                   (common.rounded_radius, common.rounded_radius)],
                                           font_size='15sp',
                                           halign='center',
                                           padding_x=common.element_sep * 2,
                                           color=get_color_from_hex('#000000'),
                                           background_color_display=get_color_from_hex('#f3f4f5'))

            btnEdit.bind(on_touch_up=self.cb_on_edit_touch_up)
            btnRemove.bind(on_touch_up=self.cb_on_remove_touch_up)

            pop_content = PopupMenuContent()
            pop_content.add_menu_item(btnEdit)
            pop_content.add_menu_item(HorizontalSeparator(height=dp(1)))
            pop_content.add_menu_item(btnRemove)

            self.pop_menu = PopMenu(value, pop_content)
            self.pop_menu.open()

    def cb_on_edit_touch_up(self, instance, value):
        if not instance.collide_point(*value.pos):
            return
        App.get_running_app().root.show_add_keyword(keyword=Keyword(text=self.text))
        self.pop_menu.dismiss()

    def cb_on_remove_touch_up(self, instance, value):
        if not instance.collide_point(*value.pos):
            return
        App.get_running_app().controller.remove_keyword(Keyword(text=self.text))
        self.pop_menu.dismiss()


class AddNewKeywordPanel(MessagePanel):
    text = StringProperty('')

    def __init__(self, keyword=None, **kwargs):
        super(AddNewKeywordPanel, self).__init__(**kwargs)

        self.keyword = keyword

        if self.keyword:
            self.old_keyword = keyword

            # Disable button save
            self.btn_save.disabled = True


class ActivationDialog(MessagePanel):
    text = StringProperty('')


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class CellItem(FloatLayout):
    description = StringProperty('')
    frequency = StringProperty('')
    is_header = BooleanProperty(False)
    is_last = BooleanProperty(False)
    color = ListProperty(get_color_from_hex('#000000'))


if __name__ == '__main__':
    SpeechQCApp().run()
