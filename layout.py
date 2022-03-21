import tkinter.messagebox
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfile

import os.path
from eds import *
from main import login_send, login_receive


class Base:
    def __init__(self, server):
        self.win = Tk()
        self.server = server

    def loop(self):
        self.win.mainloop()


class LayoutReceive(Base):
    def __init__(self, server):
        super().__init__(server)
        self.win.title("Receive email")

        er = EmailReceiver(server)
        emails = er.getEmails()

        self.files = []

        for index, e in enumerate(emails):
            frame = Frame(self.win)
            frame.pack(fill=X)

            frame_from = Frame(self.win)
            frame_from.pack(fill=X)

            frame_text = Frame(self.win)
            frame_text.pack(fill=X)

            frame_files = Frame(self.win)
            frame_files.pack(fill=X)

            lbl_subj = ttk.Label(frame, text="Subject:", width=10)
            lbl_subj_text = ttk.Label(frame, text=e['Subject'])

            lbl_from = ttk.Label(frame_from, text="From:", width=10)
            lbl_from_text = ttk.Label(frame_from, text=e['From'])

            lbl_txt = ttk.Label(frame_text, text="Text:", width=10)
            lbl_txt_text = ttk.Label(frame_text, text=e['Text'])

            str_files = ""
            files = []
            for idx, f in enumerate(e['Files']):
                file_data = f['Data']
                file_type = f['Key']
                file = {'Data': file_data, 'Type': file_type}
                files.append(file)
                str_files += f['Name']
                if idx != len(e['Files']) - 1:
                    str_files += ', '

            self.files.append(files)

            lbl_files = ttk.Label(frame_files, text="Files:")
            lbl_files_text = ttk.Label(frame_files, text=str_files)

            but_verify = ttk.Button(frame_from, text="Verify", command=lambda: self.verify(index))

            lbl_subj.pack(side=LEFT)
            lbl_subj_text.pack(side=LEFT)
            lbl_from.pack(side=LEFT)
            lbl_from_text.pack(side=LEFT)
            lbl_txt.pack(side=LEFT)
            lbl_txt_text.pack(side=LEFT)
            lbl_files.pack(side=LEFT)
            lbl_files_text.pack(side=LEFT)
            but_verify.pack(side=RIGHT)

        # index += 1

    def verify(self, index):
        values = self.files[0]
        content = ""
        public_key = ""
        signature = ""

        for v in values:
            if v['Type'] == "PUBLIC":
                public_key = v['Data']
            else:
                if v['Type'] == "SIG":
                    signature = v['Data']
                else:
                    content = v['Data']
        result = verify(public_key, content, signature)

        if result:
            tkinter.messagebox.showinfo(title="Success!", message="File was successfully verified!")
        else:
            tkinter.messagebox.showinfo(title="Error!", message="Something went wrong, and file was not successfully "
                                                                "verified!")


class LayoutSend(Base):
    def __init__(self, server):
        super().__init__(server)
        self.attachment = None
        self.win.title("Send email")

        frame = Frame(self.win)
        frame.pack(fill=X)

        frame_from = Frame(self.win)
        frame_from.pack(fill=X)

        frame_to = Frame(self.win)
        frame_to.pack(fill=X)

        frame_txt = Frame(self.win)
        frame_txt.pack(fill=X)

        frame_att = Frame(self.win)
        frame_att.pack(fill=X)

        lbl_subj = ttk.Label(frame, text="Subject", width=10)
        self.ntr_subj = ttk.Entry(frame)
        self.ntr_subj.insert(0, "Spam training")

        lbl_from = ttk.Label(frame_from, text="From", width=10)
        self.ntr_from = ttk.Entry(frame_from)
        self.ntr_from.insert(0, "Training team")

        lbl_to = ttk.Label(frame_to, text="To", width=10)
        self.ntr_to = ttk.Entry(frame_to)
        self.ntr_to.insert(0, "antsrp1t@gmail.com")

        lbl_txt = ttk.Label(frame_txt, text="Text", width=10)
        self.ntr_txt = Text(frame_txt, height=5)
        self.ntr_txt.insert("end-1c", "hello bro spam test 1 2 3 ...")

        lbl_att = ttk.Label(frame_att, text="Attach a file: ")
        but_att = ttk.Button(frame_att, text="Upload", command=lambda: self.open_file())
        self.lbl_name = ttk.Label(frame_att)

        but_send = ttk.Button(self.win, text="Send", command=lambda: self.send_email())

        lbl_subj.pack(side=LEFT)
        self.ntr_subj.pack(fill=X, padx=5, pady=5)
        lbl_from.pack(side=LEFT)
        self.ntr_from.pack(fill=X, padx=5, pady=5)
        lbl_to.pack(side=LEFT)
        self.ntr_to.pack(fill=X, padx=5, pady=5)
        lbl_txt.pack(side=LEFT, anchor=N)
        self.ntr_txt.pack(fill=BOTH, padx=5, pady=5)

        lbl_att.pack(side=LEFT)
        but_att.pack(side=LEFT)
        self.lbl_name.pack(side=LEFT)

        but_send.pack(pady=10)

        self.server = server

    def open_file(self):
        file_path = askopenfile(mode='rb')
        if file_path is not None:
            self.attachment = file_path
            self.lbl_name.config(text=os.path.basename(file_path.name))

    def send_email(self):
        subj = self.ntr_subj.get()
        msg_from = self.ntr_from.get()
        msg_to = self.ntr_to.get()
        text = self.ntr_txt.get("1.0", "end-1c")

        es = EmailSender(subj, msg_from, msg_to, text, self.attachment)
        es.add_server(self.server)
        result = es.send()

        if result:
            tkinter.messagebox.showinfo(title="Success!", message="Email was sent successfully!")


class LoginLayout:
    def __init__(self, type):
        self.win = Tk()
        self.win.title("Login")
        self.type = type

        frame = Frame(self.win)
        frame.pack(fill=X)

        frame_log = Frame(frame)
        frame_log.pack(fill=X)

        frame_pass = Frame(frame)
        frame_pass.pack(fill=X)

        frame_error = Frame(frame)
        frame_error.pack(fill=X)

        lbl_log = ttk.Label(frame_log, text="Login", width=10)
        self.ntr_log = ttk.Entry(frame_log)
        lbl_pass = ttk.Label(frame_pass, text="Password", width=10)
        self.ntr_pass = ttk.Entry(frame_pass, show="*")
        self.lbl_error = ttk.Label(frame_error, foreground='red', width=20)

        self._server = None

        but_send = ttk.Button(frame, text="Login", command=lambda: self.login())

        lbl_log.pack(side=LEFT, padx=5, pady=5)
        self.ntr_log.pack(side=LEFT, padx=5, pady=5)
        lbl_pass.pack(side=LEFT, padx=5, pady=5)
        self.ntr_pass.pack(side=LEFT, padx=5, pady=5)
        self.lbl_error.pack(padx=5, pady=5)
        but_send.pack()

    def loop(self):
        self.win.mainloop()

    def get_server(self):
        return self._server

    def login(self):
        username = self.ntr_log.get()
        password = self.ntr_pass.get()

        server = None

        if self.type == 's':
            server = login_send(username, password)
        else:
            if self.type == 'r':
                server = login_receive(username, password)
            else:
                tkinter.messagebox.showinfo(title="Error!", message="Incorrect type of operation!")

        if server is None:
            self.lbl_error.config(text="Incorrect data")
            return
        else:
            self._server = server
            self.win.destroy()

