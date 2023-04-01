import time
import os

import speech_recognition as sr
from time import sleep

from fpdf import FPDF

import common
from keys import *


class QCController:

    def __init__(self, keywords, view):
        # Model
        self.keywords = keywords

        # View
        self.view = view

    def refresh_keywords(self):
        self.keywords.refresh(self.view)

    def get_keywords(self):
        pass

    def save_keywords(self, keys):
        self.keywords.append(keys, self.view)

    def update_keyword(self, old_key, new_key):
        self.keywords.update(old_key, new_key, self.view)

    def remove_keyword(self, keywords):
        self.keywords.remove(keywords, self.view)

    def remove_all(self):
        self.keywords.remove_all(self.view)

    def transcribe_audio(self, file):
        print('Checking TC record')
        audio_file = file

        # use the audio file as the audio source
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = r.record(source)  # read the entire audio file

        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            s = '''
            thằng Kim ngốc Alo alo alo nghe máy hả Note à Dạ alo Em gọi mà làm giấy tạm khóa của mobi ví anh nốt Hay là em có nhận được cái hồ sơ của mình là hôm nay là đóng tiền cho bé nhân viên á là không biết anh đóng chưa để em làm giấy anh ở dưới bệnh viện 23 bữa nữa hả anh Ở vậy sao bé nhân viên nó báo em chiều hôm nay 4:00 đây em lên chuẩn bị làm giấy đây mà mà sao giờ hai ba ngày sao ta Giờ người thân này nọ đi đóng giùm anh đi chứ bây giờ hồ sơ của anh đó em đang đang xử lý đây đang làm giấy tới nơi rồi mà anh nói hai ba ngày là sao được Hay là mình không có mình mình đang mà đang chạy viện Phí mình không có tiền hay sao anh vậy thì anh ra lại chắc chắn là mấy nhân viên chứ để anh để mấy nhân viên nó muốn gửi hồ sơ lên tới liền Em đang làm việc cho Triệu Sơn đây mà Giờ sao anh làm sao được thì thì bên em bên em bé nhân viên không bên em bên công ty em đó là đâu có bắt ép anh đâu nói chị cho anh cái lời hứa Thôi anh hứa giúp em chắc chắn đi đằng này anh hứa mà giờ em đang chuẩn bị hồi xưa đây là tới nơi rồi giờ rồi anh nói hai ba ngày thì bên em thông cảm mà anh nằm viện Bên Em đâu nói gì đâu Nói chung nằm viện thì bên em cũng trách mình biết việc này nọ Nhưng mà anh hứa chắc chắn một tí Tại vì hồ sơ đó nó gửi đi em đây nói khách hàng yêu cầu làm giấy tất toán Em đang làm chuẩn bị đây mà thấy Thấy ti tới giờ nó chưa có gì hết Em mới gọi hỏi anh vậy nãy em gọi em la nó quá trời giờ em Em nói nốt nè bây giờ tạm thời em đang giữ hồ sơ của anh nhưng mà anh bỏ một bên được không Anh làm việc với lại bé Nhân viên sắp xếp Mình đóng sớm cho nó đi em nói chung đóng trước 28 đừng có qua ngày làm gì để bên em xử lý hồ sơ tại vì em đang làm giấy phép toán đây mà đang đang cắn cái chỗ anh đóng tiền đi mà nó báo em chiều giờ chiều nay là 4:00 anh đóng mà làm em chờ nãy giờ rồi em mới nói nó rồi Gọi anh Tài này nọ rồi anh anh sắp xếp giúp em nha trước 28 nha Có gì mấy thằng Nguyên nó làm việc của anh em giữ hồ sơ em xóa nào xấu cho tao bị xóa nó nó không phải là vào là xóa liền đâu anh xin cấp trên thẩm định nói này nói nọ nữa giữ sức khỏe nha anh Út
            '''
            if App.get_running_app().mode == 'production':
                transcript = r.recognize_google(audio, language='vi-VN')
            else:
                # Debug mode
                time.sleep(1)
                transcript = s
        except sr.UnknownValueError:
            transcript = "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            transcript = "Could not request results from Google Speech Recognition service; {0}".format(e)

        self.keywords.check_keywords(transcript.strip(), self.view)

    def export_report(self, content):
        try:
            pdf = PDF('P', format='A4')
            pdf.alias_nb_pages()
            pdf.add_page()
            pdf.add_font('DejaVu', '', os.path.join(common.get_bundle_dir(), 'font', 'DejaVuSansCondensed.ttf'), uni=True)
            pdf.add_font('DejaVu', '', os.path.join(common.get_bundle_dir(), 'font', 'DejaVuSans-Bold.ttf'), uni=True)
            pdf.set_font('DejaVu', style='', size=12)

            # Write part 1 - record name
            pdf.cell(185, 7, '1. RECORD FILE: ' + content['filename'][1], border=0, ln=1)
            # Write blank line
            pdf.cell(185, 7, '', border=0, ln=1)
            # Write part 2 - conversation
            pdf.cell(185, 7, '2. NỘI DUNG RECORD:', border=0, ln=1)
            # Write word by word
            self.write_conversation(content['transcript'], pdf)
            # Write blank line
            pdf.cell(185, 7 * 2, '', border=0, ln=1)
            # Write part 3 - Statistics
            pdf.cell(185, 7, '3. THỐNG KÊ SAI PHẠM:', border=0, ln=1)
            # Write statistics
            self.write_statistics(content['keywords'], pdf)
            # Write blank line
            pdf.cell(185, 7, '', border=0, ln=1)
            # Write end notification
            pdf.set_x(55)
            notification = 'End of report'
            pdf.cell((210 - pdf.get_string_width(notification)) / 2, 7, notification, border=0, ln=1, align='C')

            out_file = ''.join((os.path.splitext(content['filename'][1])[0], '.pdf'))
            pdf.output(out_file, 'F')
            return out_file
        except Exception:
            return False

    def write_conversation(self, s, pdf):
        words = s.split(' ')
        row_len = 10        # Left border
        for word in words:
            word, is_marked = self.parse_word(word)
            row_len += pdf.get_string_width(word + ' ')
            if is_marked:
                # Keyword
                pdf.set_text_color(255, 0, 0)
            else:
                # Not a keyword
                pdf.set_text_color(0, 0, 0)
            if row_len >= 185:
                pdf.cell(pdf.get_string_width(word + ' '), 7, word, border=0, ln=1)
                row_len = 10        # Reset length to left border
            else:
                pdf.cell(pdf.get_string_width(word + ' '), 7, word, border=0, ln=0)

        pdf.set_text_color(0, 0, 0)     # Reset text color to black

    def write_statistics(self, keywords, pdf):
        pdf.set_x(55)
        pdf.cell(50, 7, 'Keyword', border=1, ln=0, align='C')
        pdf.cell(50, 7, 'Tần suất', border=1, ln=1, align='C')
        for keyword, cnt in keywords.items():
            pdf.set_x(55)
            pdf.cell(50, 7, keyword.text, border=1, ln=0)
            pdf.cell(50, 7, str(len(cnt)), border=1, ln=1, align='C')

    @staticmethod
    def parse_word(s):
        if s.startswith('[color='):
            return s[s.find('[b]') + 3:s.find('[/b]')], True
        return s, False


class PDF(FPDF):
    def header(self):
        # Logo
        self.image(os.path.join(common.get_bundle_dir(), 'images', 'anydo_104098.png'), 10, 8, 20)
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30, 10, 'Record QC Report', 0, 0, 'C')
        # Line break
        self.ln(20)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')
