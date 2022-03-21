import argparse
import imaplib
import smtplib
import sys

from layout import *


def login_send(username, password):
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    try:
        server.login(username, password)
    except smtplib.SMTPAuthenticationError:
        print("the connection data is incorrect or access denied!")
        return None
    return server


def login_receive(username, password):
    server = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    try:
        server.login(username, password)
    except imaplib.IMAP4.error as e:
        if 'Invalid credentials' in str(e):
            print("the connection data is incorrect or access denied!")
            return None
    return server


def parse():
    parser = argparse.ArgumentParser()

    parser.add_argument('-a', dest='act', default='s', nargs=1, choices=['s', 'r'], required=True,
                        help="choose an option of program to do: send email (s) or receive email (r)")

    #if len(sys.argv) == 1:
    #    parser.print_help(sys.stderr)
    #    sys.exit(1)

    return parser.parse_args()


def main():
    args = parse()

    c_type = args.act[0]

    login_layout = LoginLayout(c_type)
    login_layout.loop()

    server = login_layout.get_server()

    if server is None:
        return

    if c_type == 's':
        # server = login_send(username, password)
        layout = LayoutSend(server)
        layout.loop()
        server.quit()
    else:
        # server = login_receive(username, password)
        layout = LayoutReceive(server)
        layout.loop()
        server.logout()


if __name__ == '__main__':
    main()
