#!/usr/bin/python3
import rrdtool
ret = rrdtool.create("/home/jrockit/Documentos/Redes/practica3/RRD/trend.rrd",
                     "--start",'N',
                     "--step",'60',
                     "DS:CPUload:GAUGE:60:0:100",
                     "DS:RAMload:GAUGE:60:0:100",
                     "DS:InOct:COUNTER:120:U:U",
                     "DS:OutOct:COUNTER:120:U:U",
                     "RRA:AVERAGE:0.5:1:24",
                     "RRA:AVERAGE:0.5:1:24",
                     "RRA:AVERAGE:0.5:1:200",
                     "RRA:AVERAGE:0.5:1:200")
if ret:
    print (rrdtool.error())
