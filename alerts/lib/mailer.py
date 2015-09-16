import smtplib
import logging
from email.mime.text import MIMEText

class Mailer(object):
    
    def __init__(self, host, port, username, password='', verbose=0):
        self.smtp = None
        self.host = host
        self.port = int(port)
        self.username = username
        self.password = password
        self.verbose = verbose

    def connect(self):
        if self.smtp:
            logging.warn(
                "Allready connected to SMTP endpoint (%s,%d)" %(self.host, self.port))
            return
        self.smtp = smtplib.SMTP_SSL()
        self.smtp.set_debuglevel(self.verbose)
        self.smtp.connect(self.host, self.port)
        self.smtp.login(self.username, self.password)
        return

    def send(self, to_addr, headers, body):
        msg = MIMEText(body.encode('utf-8'), 'html', 'utf-8')
        for h,v in headers.items():
            msg[h] = v
        if self.smtp is None:
            # Try to connect first
            self.connect()
        from_addr = self.username
        self.smtp.sendmail(from_addr, to_addr, msg.as_string())
        return

    def __del__(self):
        if self.smtp:
            self.smtp.quit()

def make_mailer(config):
    smtp_host = config.get('smtp_host', '127.0.0.1')
    smtp_port = config.get('smtp_port', '587')
    smtp_user = config.get('smtp_user')
    smtp_pass = config.get('smtp_pass')
    mailer = Mailer(host=smtp_host, port=smtp_port, username=smtp_user, password=smtp_pass)
    return mailer


