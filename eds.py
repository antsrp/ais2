import base64
import email
import os.path
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key


class EmailSender:
    def __init__(self, subj, msg_from, msg_to, text, attachment):
        self.msg = create_message(subj, msg_from, msg_to, text)
        private_key, self.public = generate()
        attach = attachment.read()
        self.signature = sign(private_key, attach)
        attach_file_to_msg(self.msg, attachment)
        attach_file_to_msg(self.msg, self.signature)
        attach_file_to_msg(self.msg, self.public)

        self.server = None

    def add_server(self, server):
        self.server = server

    def send(self):
        if self.server is not None:
            self.server.send_message(self.msg)
            return True
        return False


class EmailReceiver:
    def __init__(self, server):
        self.server = server

    def getEmails(self):
        answer = []
        select_data = self.server.select('INBOX')
        result, numbers = self.server.uid('search', None, "ALL")

        for num in numbers[0].split():
            result, data = self.server.uid('fetch', num, '(RFC822)')
            body = data[0][1]
            m = email.message_from_bytes(body)

            if m.get_content_maintype() != 'multipart':
                continue

            files = []
            sig_flag = False
            pem_flag = False

            subject = m['subject']
            msg_from = m['from']
            for part in m.walk():
                if part.get_content_maintype() == 'multipart':
                    for p in part.get_payload():
                        if p.get_content_maintype() == 'text':
                            text = p.get_payload()
                if part.get('Content-Disposition') is None:
                    continue
                filename = part.get_filename()
                key = "FILE"
                if filename is not None:
                    if filename == "signature.sig":
                        sig_flag = True
                        key = "SIG"
                    else:
                        if filename == "public.pem":
                            pem_flag = True
                            key = "PUBLIC"
                    temp = part.get_payload(decode=True)
                    file = {'Name': filename, 'Data': temp, 'Key': key}
                    files.append(file)
            if len(files) == 3 and sig_flag and pem_flag:
                ans = {'Subject': subject, 'From': msg_from, 'Text': text, 'Files': files}
                answer.append(ans)

        return answer


def attach_file_to_msg(msg, file):
    fn = os.path.basename(file.name)
    part = MIMEApplication(open(file.name, 'rb').read())
    part.add_header('Content-Disposition', 'attachment', filename=fn)
    msg.attach(part)


def create_message(subj, msg_from, msg_to, text):
    msg = MIMEMultipart()
    msg['Subject'] = subj
    msg['From'] = msg_from
    msg['To'] = msg_to

    msg.attach(MIMEText(text))

    return msg


def generate():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend(),
    )

    with open('public.pem', 'wb') as f:
        f.write(
            private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

    return private_key, f


def sign(private_key, attachment):
    signature = base64.b64encode(
        private_key.sign(
            attachment,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
    )
    with open('signature.sig', 'wb') as f:
        f.write(signature)

    return f


def verify(public_key, content, signature):
    public_key = load_pem_public_key(public_key, default_backend())

    sig = base64.b64decode(signature)
    try:
        public_key.verify(
            sig,
            content,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
    except cryptography.exceptions.InvalidSignature:
        print('ERROR: Invalid signature!')
        return False

    return True
