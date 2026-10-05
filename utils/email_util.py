import email
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl
from webbrowser import get
from settings import password_email, smtp_server_email

class email_utils:
    def __init__(self):
        self.sender_email = smtp_server_email
        self.passwrd = password_email
        self.smtp_serwer = 'smtp.gmail.com'
    def email_sent(self, email, topic, data):
        #koniguracja
        port = 465
        odbiorca = str(email)
        nadawca = self.sender_email
        temat = str(topic)
        treść = str(data)
        wiadomość = MIMEMultipart()
        wiadomość['From'] = nadawca
        wiadomość['To'] = odbiorca
        wiadomość['Subject'] = temat
        wiadomość.attach(MIMEText(treść, "plain"))
        tekst = wiadomość.as_string()
        ssl_pol = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_serwer, port, context=ssl_pol) as server:
            server.login(nadawca, self.passwrd)
            server.sendmail(nadawca, odbiorca, tekst)
        return "success"