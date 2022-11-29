#!/usr/bin/python3
import time
import rrdtool
from getSNMP import consultaSNMP
rrdpath = '/home/jrockit/Documentos/Redes/practica3/RRD/'
carga_CPU = 0
comunidad = "JRockitDesk"
hostName = "localhost"

while 1:   
    carga_CPU = int(consultaSNMP(comunidad, hostName,'1.3.6.1.2.1.25.3.3.1.2.196608'))
    
    traficoEntrada = int(consultaSNMP(comunidad, hostName,'1.3.6.1.2.1.2.2.1.10.1'))
    traficoSalida = int(consultaSNMP(comunidad, hostName,'1.3.6.1.2.1.2.2.1.16.1'))
    
    totalRAM = int(consultaSNMP(comunidad, hostName,'1.3.6.1.4.1.2021.4.5.0'))
    freeRAM = int(consultaSNMP(comunidad, hostName,'1.3.6.1.4.1.2021.4.11.0'))
    sharedRAM = int(consultaSNMP(comunidad, hostName,'1.3.6.1.4.1.2021.4.13.0'))
    buffRAM = int(consultaSNMP(comunidad, hostName,'1.3.6.1.4.1.2021.4.14.0'))
    cacheRAM = int(consultaSNMP(comunidad, hostName,'1.3.6.1.4.1.2021.4.15.0'))
    
    """ Hacemos una aproximacion de la RAM utilizada """
    usedRAM = freeRAM + sharedRAM + (buffRAM / cacheRAM)
    
    """
    Sacamos porcentaje 
    RAM TOTAL   -> 100%
    RAM USADA   -> ?%
    """
    cargaRAM = (usedRAM * 100) / totalRAM
    
    """ valor = "N:" + str(carga_CPU) """
    valor = "N:" + str(carga_CPU) + ':' + str(cargaRAM) + ':' + str(traficoEntrada) + ':' + str(traficoSalida)
    
    print (valor)
    rrdtool.update(rrdpath+'trend.rrd', valor)
    time.sleep(5)

if ret:
    print (rrdtool.error())
    time.sleep(300)
