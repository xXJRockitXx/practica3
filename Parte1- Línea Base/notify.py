#!/usr/bin/python3
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

COMMASPACE = ', '
# Define params
rrdpath = '/home/jrockit/Documentos/Redes/practica3/RRD/'
imgpath = '/home/jrockit/Documentos/Redes/practica3/IMG/'
fname = 'trend.rrd'

mailsender = "cruzadrian342@gmail.com"
mailreceip = "cruzadrian342@gmail.com"
mailserver = 'smtp.gmail.com: 587'
password = 'kfaqvngdqvshsxhi'

def send_alert_attached(subject):
    """ Envía un correo electrónico adjuntando la imagen en IMG
    """
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = mailsender
    msg['To'] = mailreceip
    fp = open(imgpath+'deteccion.png', 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    msg.attach(img)
    s = smtplib.SMTP(mailserver)

    s.starttls()
    # Login Credentials for sending the mail
    s.login(mailsender, password)

    s.sendmail(mailsender, mailreceip, msg.as_string())
    s.quit()
    
send_alert_attached("HOLA")