#!/usr/bin/python3
import sys
import rrdtool
import time
import datetime
from  notify import send_alert_attached
import time
rrdpath = '/home/jrockit/Documentos/Redes/practica3/RRD/'
imgpath = '/home/jrockit/Documentos/Redes/practica3/IMG/'

def generarGrafica(ultima_lectura):
    tiempo_final = int(ultima_lectura)
    tiempo_inicial = tiempo_final - 1800
    ret = rrdtool.graphv( imgpath+"cpu.png",
                     "--start",str(tiempo_inicial),
                     "--end",str(tiempo_final),
                     "--vertical-label=Cpu load",
                    '--lower-limit', '0',
                    '--upper-limit', '100',
                    "--title=Carga del CPU del agente Usando SNMP y RRDtools \n Detección de umbrales",
                    "DEF:cargaCPU="+rrdpath+"trend.rrd:CPUload:AVERAGE",
                     "VDEF:cargaMAX=cargaCPU,MAXIMUM",
                     "VDEF:cargaMIN=cargaCPU,MINIMUM",
                     "VDEF:cargaSTDEV=cargaCPU,STDEV",
                     "VDEF:cargaLAST=cargaCPU,LAST",
                     "CDEF:umbral50=cargaCPU,50,LT,0,cargaCPU,IF",
                     "AREA:cargaCPU#00FF00:Carga del CPU",
                     "AREA:umbral50#FF9F00:Carga CPU mayor de 50",
                     "HRULE:50#FF0000:Umbral  50%",
                     "PRINT:cargaLAST:%6.2lf",
                     "GPRINT:cargaMIN:%6.2lf %SMIN",
                     "GPRINT:cargaSTDEV:%6.2lf %SSTDEV",
                     "GPRINT:cargaLAST:%6.2lf %SLAST" )
    print (ret)

while (1):
    ultima_actualizacion = rrdtool.lastupdate(rrdpath + "trend.rrd")
    timestamp=ultima_actualizacion['date'].timestamp()
    dato=ultima_actualizacion['ds']["CPUload"]
    print(dato)
    if dato> 50:
        generarGrafica(int(timestamp))
        send_alert_attached("Sobrepasa el umbral")
        print("sobrepasa el umbral")
    time.sleep(20)