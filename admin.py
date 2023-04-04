# This package generates activation key for users
import hashlib
import email
import imaplib
from datetime import datetime
import csv
import os


class RecordQCAdmin:

    email = 'no-reply@plusdebt.asia'
    password = 'dhf28xK7JA'
    server = 'mail9051.maychuemail.com'

    def generate_keys(self, reqs):
        d = datetime.today().strftime('%Y%m%d')
        filename = f'activation_requests_{d}.csv'
        filename = self.create_file_name(os.path.join('.', filename))
        with open(filename, 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Machine', 'User', 'Key'])
            cnt = 0
            for req in reqs:
                machine, user = req
                writer.writerow([machine, user, self.generate_activation_key(*req)])
                cnt += 1
        print(f'There are {cnt} activation requests in {filename}')

    def create_file_name(self, filepath):
        if not os.path.exists(filepath):
            return filepath
        else:
            path, filename = os.path.split(filepath)
            name, ext = os.path.splitext(filename)
            if len(name) == 28:
                suffix = 1
            else:
                suffix = int(name[29:]) + 1
            new_name = self.create_file_name(os.path.join(path, ''.join((name[:28], '_', str(suffix), ext))))
            return new_name

    @staticmethod
    def generate_activation_key(machine, user):
        seed = '{}{}'.format(machine, user)
        result = hashlib.md5(seed.encode())
        return result.hexdigest().upper()

    def check_mail(self):
        # connect to the server and go to its inbox
        mail = imaplib.IMAP4_SSL(self.server)
        mail.login(self.email, self.password)
        # we choose the inbox but you can select others
        mail.select('inbox')

        # we'll search using the ALL criteria to retrieve
        # every message inside the inbox
        # it will return with its status and a list of ids
        # status, data = mail.search(None, 'ALL')
        status, data = mail.search(None, 'UNSEEN')
        # the list returned is a list of bytes separated
        # by white spaces on this format: [b'1 2 3', b'4 5 6']
        # so, to separate it first we create an empty list
        mail_ids = []
        # then we go through the list splitting its blocks
        # of bytes and appending to the mail_ids list
        for block in data:
            # the split function called without parameter
            # transforms the text or bytes into a list using
            # as separator the white spaces:
            # b'1 2 3'.split() => [b'1', b'2', b'3']
            mail_ids += block.split()

        # now for every id we'll fetch the email
        # to extract its content
        activation_reqs = []
        for i in mail_ids:
            # the fetch function fetch the email given its id
            # and format that you want the message to be
            status, data = mail.fetch(i, '(RFC822)')

            # the content data at the '(RFC822)' format comes on
            # a list with a tuple with header, content, and the closing
            # byte b')'
            for response_part in data:
                # so if its a tuple...
                if isinstance(response_part, tuple):
                    # we go for the content at its second element
                    # skipping the header at the first and the closing
                    # at the third
                    message = email.message_from_bytes(response_part[1])

                    # with the content we can extract the info about
                    # who sent the message and its subject
                    mail_from = message['from']
                    mail_subject = message['subject']

                    # then for the text we have a little more work to do
                    # because it can be in plain text or multipart
                    # if its not plain text we need to separate the message
                    # from its annexes to get the text
                    if message.is_multipart():
                        mail_content = ''

                        # on multipart we have the text message and
                        # another things like annex, and html version
                        # of the message, in that case we loop through
                        # the email payload
                        for part in message.get_payload():
                            # if the content type is text/plain
                            # we extract it
                            if part.get_content_type() == 'text/plain':
                                mail_content += part.get_payload()
                    else:
                        # if the message isn't multipart, just extract it
                        mail_content = message.get_payload()

                    # and then let's show its result
                    if mail_subject.startswith('Record QC activation request'):
                        activation_reqs.append((mail_content[mail_content.find('ID:') + 4: mail_content.find('User:')].strip(),
                                                mail_content[mail_content.find('User:') + 6:].strip()))
        return activation_reqs


if __name__ == '__main__':
    admin = RecordQCAdmin()
    admin.generate_keys(admin.check_mail())
    print('done')
