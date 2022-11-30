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
    
    fpcpu = open(imgpath+'cpu.png', 'rb')
    fpram = open(imgpath+'ram.png', 'rb')
    fpentrada = open(imgpath+'traficoEntrada.png', 'rb')
    fpsalida = open(imgpath+'traficoSalida.png', 'rb')
    
    imgcpu = MIMEImage(fpcpu.read())
    imgram = MIMEImage(fpram.read())
    imgentrada = MIMEImage(fpentrada.read())
    imgsalida = MIMEImage(fpsalida.read())
    
    fpcpu.close()
    fpram.close()
    fpentrada.close()
    fpsalida.close()
    
    msg.attach(imgcpu)
    msg.attach(imgram)
    msg.attach(imgentrada)
    msg.attach(imgsalida)
    
    s = smtplib.SMTP(mailserver)

    s.starttls()
    # Login Credentials for sending the mail
    s.login(mailsender, password)

    s.sendmail(mailsender, mailreceip, msg.as_string())
    s.quit()