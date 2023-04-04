import hashlib
import json
import os.path
import smtplib
import ssl

import wmi


class Activation:
    def send_mail(self, message):
        port = 465  # For SSL
        smtp_server = "mail9051.maychuemail.com"
        sender_email = "no-reply@plusdebt.asia"  # Enter your address
        receiver_email = "no-reply@plusdebt.asia"  # Enter receiver address
        password = 'dhf28xK7JA'

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)
            print('Sent mail successfully')
            return True
        except Exception as e:
            print(e)
        return False

    @staticmethod
    def read_hd_serial():
        c = wmi.WMI()
        for item in c.Win32_PhysicalMedia():
            if 'PHYSICALDRIVE0' in item.Tag:
                return item.SerialNumber.strip()
        return ''

    def create_activation_key(self, seed):
        result = hashlib.md5(seed.encode())
        return result.hexdigest().upper()

    def check_activation(self, view):
        view.activate(self.is_activated())

    def validate_info(self, contact, view):
        subject = 'Record QC activation request - {}'.format(contact)
        content = """
        ID: {}
        User: {}""".format(self.read_hd_serial(), contact)
        message = 'Subject: {}\n\n{}'.format(subject, content)
        self.contact = contact
        success = self.send_mail(message)
        view.after_validate_info(success)

    def verify_credential(self, key, view):
        expected_key = self.create_activation_key(self.read_hd_serial() + self.contact)
        is_activated = expected_key == key
        if is_activated:
            # Save credential
            with open('activation.json', 'w') as f:
                credential = {"key": key, "contact":  self.contact}
                json.dump(credential, f)
        del self.contact
        view.process_credential(is_activated)

    def is_activated(self):
        if not os.path.exists(os.path.join('.', 'activation.json')):
            # Not activated
            return False

        # Check activation key
        with open(os.path.join('.', 'activation.json')) as f:
            try:
                info = json.load(f)
            except json.JSONDecodeError:
                # Activation credential error
                return False

        try:
            expected_key = self.create_activation_key(self.read_hd_serial() + info['contact'])
            if expected_key == info['key']:
                # Activated
                return True
        except KeyError:
            # No information in key file
            return False
        # Not activated
        return False
