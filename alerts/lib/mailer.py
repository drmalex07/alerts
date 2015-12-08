import smtplib
import logging
from email.mime.text import MIMEText

class Mailer(object):
    
    SSL_PORTS = [465]
    
    verbose = False

    def __init__(self, host, port, username, password, from_addr='', verbose=None):
        self.smtp = None
        self.host = host
        self.port = int(port)
        self.username = username
        self.password = password
        self.from_addr = from_addr or username
        
        if not (verbose is None): 
            self.verbose = bool(verbose)

    def connect(self):
        if self.smtp:
            logging.warn(
                "Allready connected to SMTP endpoint (%s,%d)" % (
                    self.host, self.port))
            return
        
        # Follow port conventions to guess SMTP connection protocol
        use_ssl = False
        if self.port in self.SSL_PORTS:
            self.smtp = smtplib.SMTP_SSL()
            use_ssl = True
        else:
            self.smtp = smtplib.SMTP();

        self.smtp.set_debuglevel(self.verbose)
        self.smtp.connect(self.host, self.port)
        
        if not use_ssl:
            # Complete the STARTTLS handshake
            self.smtp.starttls()

        self.smtp.login(self.username, self.password)
        return

    def send(self, to_addr, headers, body):
        
        if isinstance(body, unicode):
            body = body.encode('utf-8')
        else:
            # Assume is encoded as utf8
            pass
        
        msg = MIMEText(body, 'html', 'utf-8')
        msg['Content-Type'] = 'text/html; charset=utf-8'

        # Update message with custom headers
        for h,v in headers.items():
            msg[h] = v
        
        if self.smtp is None:
            # Try to connect first
            self.connect()
        from_addr = self.from_addr
        
        # Send on the wire
        self.smtp.sendmail(from_addr, to_addr, msg.as_string())
        return

    def __del__(self):
        if self.smtp:
            self.smtp.quit()

def make_mailer(config):
    smtp_host = config.get('smtp_host', '127.0.0.1')
    smtp_port = config.get('smtp_port', '465') # SMTP over SSL
    smtp_user = config.get('smtp_user', '')
    smtp_pass = config.get('smtp_pass', '')
    from_addr = config.get('from')
    mailer = Mailer(
        host = smtp_host,
        port = smtp_port,
        username = smtp_user,
        password = smtp_pass,
        from_addr = from_addr
    )
    return mailer


