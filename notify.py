#!/usr/bin/python3
import smtplib
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from getSNMP import consultaSNMP

COMMASPACE = ', '
# Define params
rrdpath = '/home/jrockit/Documentos/Redes/practica3/RRD/'
imgpath = '/home/jrockit/Documentos/Redes/practica3/IMG/'
fname = 'trend.rrd'

mailsender = "cruzadrian342@gmail.com"
mailreceip = "cruzadrian342@gmail.com"
mailserver = 'smtp.gmail.com: 587'
password = 'kfaqvngdqvshsxhi'

""" mailsender = "dummycuenta3@gmail.com"
mailreceip = "dummycuenta3@gmail.com"
mailserver = 'smtp.gmail.com: 587'
password = 'dvduuffmlhspbmjj' """

comunidad = "LuisAlbertoGarcia"
hostName = "localhost"

nombre = consultaSNMP(comunidad, hostName,'1.3.6.1.2.1.1.5.0')
so = consultaSNMP(comunidad, hostName,'1.3.6.1.2.1.1.1.0')
tiempo = consultaSNMP(comunidad, hostName,'1.3.6.1.2.1.25.1.1.0')
fechaHora = consultaSNMP(comunidad, hostName,'1.3.6.1.2.1.25.1.2.0')

mensaje = "Nombre: " + str(nombre) + "\nSistema operativo: " + str(so) + "\nTiempo de ejecucion: " + str(tiempo) + "s\nFecha y Hora del host: " + str(fechaHora)
""" print(mensaje) """
COMMASPACE = ', '

def send_alert_attached(subject):
    """ Envía un correo electrónico adjuntando la imagen en IMG
    """
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = mailsender
    msg['To'] = mailreceip
    
    fpcpu = open(imgpath+'cpu.png', 'rb')
    """ fpram = open(imgpath+'ram.png', 'rb')
    fpentrada = open(imgpath+'traficoEntrada.png', 'rb')
    fpsalida = open(imgpath+'traficoSalida.png', 'rb') """
    
    imgcpu = MIMEImage(fpcpu.read())
    """ imgram = MIMEImage(fpram.read())
    imgentrada = MIMEImage(fpentrada.read())
    imgsalida = MIMEImage(fpsalida.read()) """
    
    fpcpu.close()
    """ fpram.close()
    fpentrada.close()
    fpsalida.close() """
    
    
    msg.attach(MIMEText(mensaje,'plain'))
    msg.attach(imgcpu)
    """ msg.attach(imgram)
    msg.attach(imgentrada)
    msg.attach(imgsalida) """
    
    s = smtplib.SMTP(mailserver)

    s.starttls()
    # Login Credentials for sending the mail
    s.login(mailsender, password)

    s.sendmail(mailsender, mailreceip, msg.as_string())
    s.quit()
    
""" send_alert_attached("Sobrepasa el umbral") """