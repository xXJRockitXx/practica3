#!/usr/bin/python3
import os
import rrdtool
import time
from fpdf import FPDF
from base64 import decode
from datetime import datetime
from pysnmp.hlapi import *
from threading import *
from  notify import send_alert_attached
from email.mime.text import MIMEText

rrdpath = '/home/jrockit/Documentos/Redes/practica3/RRD/'
imgpath = '/home/jrockit/Documentos/Redes/practica3/IMG/'

"""

RAM TOTAL Kylobytes:
snmpget -v 1 -c LuisAlbertoGarcia localhost .1.3.6.1.4.1.2021.4.5.0
snmpget -v 1 -c JRockitDesk localhost .1.3.6.1.4.1.2021.4.5.0
                                      .1.3.6.1.4.1.2021.4.5
RAM Usada:
snmpget -v 1 -c LuisAlbertoGarcia localhost .1.3.6.1.4.1.2021.4.6.0
snmpget -v 1 -c JRockitDesk localhost .1.3.6.1.4.1.2021.4.6.0

Total RAM Free: 
snmpget -v 1 -c LuisAlbertoGarcia localhost .1.3.6.1.4.1.2021.4.11.0
snmpget -v 1 -c JRockitDesk localhost .1.3.6.1.4.1.2021.4.11.0

Total RAM Shared: 
snmpget -v 1 -c LuisAlbertoGarcia localhost .1.3.6.1.4.1.2021.4.13.0
snmpget -v 1 -c JRockitDesk localhost .1.3.6.1.4.1.2021.4.13.0

Total RAM Buffered: 
snmpget -v 1 -c LuisAlbertoGarcia localhost .1.3.6.1.4.1.2021.4.14.0
snmpget -v 1 -c JRockitDesk localhost .1.3.6.1.4.1.2021.4.14.0

Total RAM Cache:
snmpget -v 1 -c LuisAlbertoGarcia localhost .1.3.6.1.4.1.2021.4.15.0
snmpget -v 1 -c JRockitDesk localhost .1.3.6.1.4.1.2021.4.15.0

MAGIA:
snmpwalk -c JRockitDesk -v 2c localhost .1.3.6.1.4.1.2021.4
snmpwalk -c LuisAlbertoGarcia -v 2c localhost .1.3.6.1.4.1.2021.4

MEMORIA USADA es free + shared + (buff / cache) 
xd = free + buff + cache + shared
USADA = total - xd

FEHCA Y HORA 
snmpget -v 1 -c JRockitDesk localhost 1.3.6.1.2.1.25.1.2.0

TIEMPO DE ACTIVIDAD:
snmpget -v 1 -c JRockitDesk localhost 1.3.6.1.2.1.25.1.1.0

IN:
snmpget -v 1 -c JRockitDesk localhost 1.3.6.1.2.1.2.2.1.10.x

OUT:
snmpget -v 1 -c JRockitDesk localhost 1.3.6.1.2.1.2.2.1.16.x

"""

class Agente:
    """ Clase para el manejo de los Agentes """
    def __init__(self, hostname, puerto, comunidad, vSNMP):
        self.hostname = hostname
        self.puerto = puerto
        self.comunidad = comunidad
        self.vSNMP = vSNMP
        self.win = False

    def ip_hostname(self):
        """ Devolvemos el ip/hostname del agente """
        return self.hostname
    
    def datos(self):
        """ Devolvemos datos del agente: ip/hostname, puerto, comunidad """
        datos = "IP/Hostname: " + self.ip_hostname() + "\nPuerto: " + str(
            self.puerto
        ) + "\nComunidad: " + self.comunidad + "\nVersion SNMP: " + self.vSNMP + "\n\n"
        return datos

    def modificar(self, hostname, puerto, comunidad, vSNMP):
        """ Modificamos los datos de un agente """
        self.hostname = hostname
        self.puerto = puerto
        self.comunidad = comunidad
        self.vSNMP = vSNMP

    def obtener_so(self):
        """ Hacemos una consulta para obtener el sistema operativo """
        consulta = consultaSNMP(self.comunidad, self.hostname, "1.3.6.1.2.1.1.1.0")

        if (consulta == "Windows 10"):
            self.win = True
        else:
            self.win = False

        return "Sistema operativo: " + consulta

    def obtener_nombre(self):
        """ Hacemos una consulta para obtener el nombre del dispositivo """
        consulta = consultaSNMP(self.comunidad, self.hostname, "1.3.6.1.2.1.1.5.0")
        return "\nNombre del dispositivo: " + consulta

    def obtener_contacto(self):
        """ Hacemos una consulta para obtener la información de contacto """
        consulta = consultaSNMP(self.comunidad, self.hostname, "1.3.6.1.2.1.1.4.0")
        return "\n1: " + consulta
    
    def tiempo_actividad(self):
        """ Hacemos una consulta para el tiempo de actividad del sistema """
        consulta = consultaSNMP(self.comunidad, self.hostname, "1.3.6.1.2.1.25.1.1.0")
        return "\nTiempo de Actividad: " + consulta
    
    def fecha_hora(self):
        """ Hacemos una consulta para la fecha y hora del sistema """
        consulta = consultaSNMP(self.comunidad, self.hostname, "1.3.6.1.2.1.25.1.2.0")
        return "\nFecha y Hora: " + consulta

    def consultas_agente(self):
        consultasTxt = open("consultas.txt", "w")

        insertar_txt(consultasTxt, self.obtener_nombre())
        insertar_txt(consultasTxt, "\n" + self.obtener_so())
        insertar_txt(consultasTxt, "\n" + self.tiempo_actividad())
        insertar_txt(consultasTxt, "\n" + self.fecha_hora())

        consultasTxt.close()

class PDF(FPDF):
    """ Clase para manejar el diseño del PDF """
    pass

    def logo(self, nombre, x, y, w, h):
        self.image(nombre, x, y, w, h)

    def texto(self, nombre, x, y):
        with open(nombre, "rb") as xy:
            txt = xy.read().decode("latin-1")

        self.set_xy(x, y)
        self.set_text_color(0, 0, 0)
        self.set_font("Arial", '', 12)
        self.multi_cell(0, 5, txt)

    def titulos(self, titulo, x, y):
        self.set_xy(x, y)
        self.set_font("Arial", 'B', 20)
        self.set_text_color(0, 0, 0)
        self.cell(w=210.0, h=40.0, align='C', txt=titulo, border=0)
        
        
def borrar_txt():
    """ Borramos los archivos .txt que generamos para 
    desarrollar el PDF """
    archivos = os.listdir()

    for archivo in archivos:
        if (archivo.endswith(".txt")):
            os.remove(archivo)
        
        
def limpiar_pantalla():
    """ Limpiamos la terminal """
    os.system("clear")


def pausar():
    """ Esperamos a que se presione ENTER para continuar
    con el programa """
    input("\nPRESIONE ENTER PARA CONTINUAR...")
    
    
def fecha_actual(now):
    """ Devolvemos la fecha actual como cadena en formato: 
    día, mes año """
    return now.date().strftime('%d%m%Y')


def hora_actual(now):
    """ Devolvemos la hora actual como cadena en formato: 
    hora, minuto, segundo """
    return now.time().strftime('%H%M%S')


def desplegar_menu():
    """ Mostramos el menú al usuario """
    limpiar_pantalla()
    print("Sistema de Administración de Red")
    print("Práctica 3")
    print("Luis Alberto García Mejía \tGrupo: 4CM13 \tBoleta: 2020630178\n")
    print("Hola, elige una opción\n")
    print("1. Agregar Agente")
    print("2. Modificar Agente")
    print("3. Eliminar Agente")
    print("4. Generar Reporte")
    print("5. Salir")

    return int(input("\nOPCION: "))


def solicitar_datos():
    """ Solicitamos los datos del agente """
    datos = {}

    print("Ingresa los datos del agente\n")
    datos["hostname"] = input("IP/Hostname: ")
    datos["puerto"] = int(input("Puerto: "))
    datos["comunidad"] = input("Comunidad: ")
    datos["vSNMP"] = input("Versión de SNMP: ")

    return datos


def crear_agente(agentes):
    """ Creamos un nuevo agente, solcitamos sus datos y lo agregamos
    a la lista de agentes """
    limpiar_pantalla()

    datos_agente = solicitar_datos()
    agentes.append(Agente(**datos_agente))

    print("\nAgente agregado")
    pausar()


def modificar_agente(agentes):
    """ Buscamos el ip/hostname ingresado en la lista de Agentes,
    si lo encuentra, solicita datos para modificarlo """
    limpiar_pantalla()

    print("Ingresa el IP/Hostname del agente que quieras modificar datos")
    host = input("\nAgente: ")

    for agente in agentes:
        if agente.ip_hostname() == host:
            datos = solicitar_datos()
            agente.modificar(**datos)
            break

    pausar()


def buscar_hostname(agentes):
    """ Buscamos el ip/hostname ingresado en la lista de Agentes,
    si lo encuentra, lo elimina """
    limpiar_pantalla()

    print("Ingresa la IP/Hostname del Agente a eliminar\n")
    host = input("IP/Hostname: ")

    posicion = 0

    for agente in agentes:
        if agente.ip_hostname() == host:
            agentes.pop(posicion)
            break
        else:
            posicion += 1

    print("\nAgente eliminado")
    pausar()


def insertar_txt(archivo, texto):
    """ Agregamos texto información dentro del archivo .txt """
    archivo.write(texto)
    
    
def consultaSNMP(comunidad, host, oid):
    """ Funciona similar a:
|   $ snmpget -v1 -c comunidadASR localhost 1.3.6.1.2.1.1.1.0 """
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(), CommunityData(comunidad),
               UdpTransportTarget((host, 161)), ContextData(),
               ObjectType(ObjectIdentity(oid))))

    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' %
              (errorStatus.prettyPrint(),
               errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            varB = (' = '.join([x.prettyPrint() for x in varBind]))
            resultado = varB.split()[2]

    if (resultado == "Hardware:"):
        return "Windows 10"
    else:
        return resultado


def graficar(dato, imagen, vertical, titulo, ds, max, color, linea, epochInicio, epochFinal):
    """ Comenzamos a graficar, mandamos toda la información para hacer una grafica con rrdtool """   
    ret = rrdtool.graphv(imagen + ".png",
                        "--start",str(epochInicio),
                        "--end",str(epochFinal),
                        "--vertical-label=" + vertical,
                        "--title=" + titulo,
                        "DEF:sDato=segmentosRed.rrd:" + ds + ":AVERAGE",
                        "VDEF:sDatoLast=sDato,LAST",
                        "VDEF:segEntradaMax=sDato,MAXIMUM",
                        "CDEF:Nivel1=sDato,7,GT,0,sDato,IF",
                        "PRINT:sDatoLast:%6.2lf",
                        "GPRINT:segEntradaMax:%6.2lf %S " + max,
                        "LINE3:sDato" + color + ":" + linea)
    
    
def nueva_pagina(pdf):
    """ Generamos una nueva pagina, colocamos encabezado y datos """
    pdf.logo("escom.png", 2, 2, 35, 25)
    pdf.titulos("Administracion de Servicios en Red", 0.0, 0.0)
    pdf.titulos("Practica 3", 0.0, 10.0)
    pdf.titulos("Luis Alberto Garcia Mejia | 4CM13", 0.0, 20.0)
    
    return pdf

def insertar_graficas(pdf):
    pdf.logo("escom.png", 2, 2, 35, 25)
    pdf.logo("multicast.png", 20, 50, 70, 40)
    pdf.logo("paquetesIp.png", 20, 95, 70, 40)
    pdf.logo("icmp.png", 20, 140, 70, 40)
    pdf.logo("segmentos.png", 20, 185, 70, 40)
    pdf.logo("datagramas.png", 20, 230, 70, 40)
    """ return pdf  """

    
def generar_reporte(agentes):
    """ Buscamos el ip/hostname del agente seleccionado, agregamos
    sus datos en un archivo de texto. Luego usamos ese .txt para
    generar el reporte en PDF, que sera nombrado en base a la fecha
    y hora """
    now = datetime.now()

    limpiar_pantalla()

    archivoTxt = open("agente.txt", "w")
    posicion = 0
    nAgente = 1

    print("Ingresa la IP/Hostname del agente que quieres el reporte\n")
    for agente in agentes:
        print(f'{nAgente}. {agente.ip_hostname()}')
        nAgente += 1

    agenteSeleccionado = input("\nAgente: ")

    for agente in agentes:
        if agente.ip_hostname() == agenteSeleccionado:
            agente.consultas_agente()
            insertar_txt(archivoTxt, agente.datos())
            archivoTxt.close()
            break
        else:
            posicion += 1

    pdf = PDF()
    pdf.add_page()
    nueva_pagina(pdf)
    pdf.texto("agente.txt", 10.0, 60.0)
    pdf.texto("consultas.txt", 10.0, 90.0)
    pdf.set_author("Luis Alberto García Mejía")
    pdf.add_page()
    pdf = nueva_pagina(pdf)
    insertar_graficas(pdf)
    pdf.output("reporte_" + fecha_actual(now) + "_" + hora_actual(now) + ".pdf", 'F')
    print("\nReporte generado!")
    borrar_txt()
    pausar()
    

def grafica_cpu(ultima_lectura):
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
                     
                     "CDEF:umbral25=cargaCPU,25,LT,0,cargaCPU,IF",
                     "AREA:cargaCPU#00FF00:Carga del CPU",
                     
                     "AREA:umbral25#abebc6:Carga CPU mayor de 25",
                     "HRULE:25#2ecc71:Umbral  25%",
                     
                     "CDEF:umbral50=cargaCPU,50,LT,0,cargaCPU,IF",
                     "AREA:umbral50#f9e79f:Carga CPU mayor de 50",
                     "HRULE:50#f1c40f:Umbral  50%",
                     
                     "CDEF:umbral75=cargaCPU,75,LT,0,cargaCPU,IF",
                     "AREA:umbral75#FF9F00:Carga CPU mayor de 75",
                     "HRULE:75#FF0000:Umbral  75%",
                     
                     "PRINT:cargaLAST:%6.2lf",
                     "GPRINT:cargaMIN:%6.2lf %SMIN",
                     "GPRINT:cargaSTDEV:%6.2lf %SSTDEV",
                     "GPRINT:cargaLAST:%6.2lf %SLAST" )
    

def graficar_ram(ultima_lectura):
    tiempo_final = int(ultima_lectura)
    tiempo_inicial = tiempo_final - 1800
    ret = rrdtool.graphv( imgpath+"ram.png",
                     "--start",str(tiempo_inicial),
                     "--end",str(tiempo_final),
                     "--vertical-label=Cpu load",
                    '--lower-limit', '0',
                    '--upper-limit', '100',
                    "--title=Carga de la RAM del agente Usando SNMP \n Detección de umbrales",
                    "DEF:cargaRAM="+rrdpath+"trend.rrd:RAMload:AVERAGE",
                     "VDEF:cargaMAX=cargaRAM,MAXIMUM",
                     "VDEF:cargaMIN=cargaRAM,MINIMUM",
                     "VDEF:cargaSTDEV=cargaRAM,STDEV",
                     "VDEF:cargaLAST=cargaRAM,LAST",
                     
                     "CDEF:umbral25=cargaRAM,25,LT,0,cargaRAM,IF",
                     "AREA:cargaRAM#00FF00:Carga de la RAM",
                     
                     "AREA:umbral25#abebc6:Carga RAM mayor de 25",
                     "HRULE:25#2ecc71:Umbral  25%",
                     
                     "CDEF:umbral50=cargaRAM,50,LT,0,cargaRAM,IF",
                     "AREA:umbral50#f9e79f:Carga RAM mayor de 50",
                     "HRULE:50#f1c40f:Umbral  50%",
                     
                     "CDEF:umbral75=cargaRAM,75,LT,0,cargaRAM,IF",
                     "AREA:umbral75#FF9F00:Carga RAM mayor de 75",
                     "HRULE:75#FF0000:Umbral  75%",
                     
                     "PRINT:cargaLAST:%6.2lf",
                     "GPRINT:cargaMIN:%6.2lf %SMIN",
                     "GPRINT:cargaSTDEV:%6.2lf %SSTDEV",
                     "GPRINT:cargaLAST:%6.2lf %SLAST" )
    
    
def graficar_entrada(ultima_lectura):
    tiempo_final = int(ultima_lectura)
    tiempo_inicial = tiempo_final - 1800
    ret = rrdtool.graphv( imgpath+"traficoEntrada.png",
                     "--start",str(tiempo_inicial),
                     "--end",str(tiempo_final),
                     "--vertical-label=Bytes/s",
                     "--title=Tráfico de Red (ENTRADA) de un agente \n Usando SNMP",
                     "DEF:traficoEntrada="+rrdpath+"trend.rrd:InOct:AVERAGE",
                     "CDEF:escalaIn=traficoEntrada,8,*",
                     "VDEF:cargaMAX=traficoEntrada,MAXIMUM",
                     "VDEF:cargaMIN=traficoEntrada,MINIMUM",
                     "VDEF:cargaSTDEV=traficoEntrada,STDEV",
                     "VDEF:cargaLAST=traficoEntrada,LAST",
                     
                     
                     "CDEF:umbral1500=escalaIn,1500,LT,0,escalaIn,IF",
                     "LINE1:escalaIn#00FF00:Tráfico de entrada",
                     
                     "LINE1:umbral1500#abebc6:Carga escalaIn mayor de 1500",
                     "HRULE:1500#2ecc71:Umbral  1500",
                     
                     "CDEF:umbral2500=escalaIn,2500,LT,0,escalaIn,IF",
                     "LINE1:umbral2500#f9e79f:Trafico Entrada mayor de 2500",
                     "HRULE:2500#f1c40f:Umbral  2500",
                     
                     "CDEF:umbral4000=escalaIn,4000,LT,0,escalaIn,IF",
                     "LINE1:umbral4000#FF9F00:Trafico Entrada mayor de 4000",
                     "HRULE:4000#FF0000:Umbral  4000",
                     
                     "PRINT:cargaLAST:%6.2lf",
                     "GPRINT:cargaMIN:%6.2lf %SMIN",
                     "GPRINT:cargaSTDEV:%6.2lf %SSTDEV",
                     "GPRINT:cargaLAST:%6.2lf %SLAST" )
    
    
def graficar_salida(ultima_lectura):
    tiempo_final = int(ultima_lectura)
    tiempo_inicial = tiempo_final - 1800
    ret = rrdtool.graphv( imgpath+"traficoSalida.png",
                     "--start",str(tiempo_inicial),
                     "--end",str(tiempo_final),
                     "--vertical-label=Bytes/s",
                     "--title=Tráfico de Red (SALIDA) de un agente \n Usando SNMP",
                     "DEF:traficoSalida="+rrdpath+"trend.rrd:OutOct:AVERAGE",
                     "CDEF:escalaOut=traficoSalida,8,*",
                     "VDEF:cargaMAX=traficoSalida,MAXIMUM",
                     "VDEF:cargaMIN=traficoSalida,MINIMUM",
                     "VDEF:cargaSTDEV=traficoSalida,STDEV",
                     "VDEF:cargaLAST=traficoSalida,LAST",
                     
                     
                     "CDEF:umbral1500=escalaOut,1500,LT,0,escalaOut,IF",
                     "LINE3:escalaOut#00FF00:Tráfico de salida",
                     
                     "LINE3:umbral1500#abebc6:Carga traficoSalida mayor de 1500",
                     "HRULE:1500#2ecc71:Umbral  1500",
                     
                     "CDEF:umbral2500=escalaOut,2500,LT,0,escalaOut,IF",
                     "LINE3:umbral2500#f9e79f:Trafico Salida mayor de 2500",
                     "HRULE:2500#f1c40f:Umbral  2500",
                     
                     "CDEF:umbral4000=escalaOut,4000,LT,0,escalaOut,IF",
                     "LINE3:umbral4000#FF9F00:Trafico Salida mayor de 4000",
                     "HRULE:4000#FF0000:Umbral  4000",
                     
                     "PRINT:cargaLAST:%6.2lf",
                     "GPRINT:cargaMIN:%6.2lf %SMIN",
                     "GPRINT:cargaSTDEV:%6.2lf %SSTDEV",
                     "GPRINT:cargaLAST:%6.2lf %SLAST" )
    

def monitorizar():
    """ monitoreo_cpu = Thread(target=cpu, name="Cpu", daemon=True)
    
    monitoreo_ram = Thread(target=ram, name="Ram", daemon=True)
    
    monitoreo_entrada = Thread(target=entrada, name="Entrada", daemon=True)
    
    monitoreo_salida = Thread(target=salida, name="Salida", daemon=True) """
    
    monitoreo_cpu = Thread(target=cpu, name="Cpu")
    
    """ monitoreo_ram = Thread(target=ram, name="Ram")
    
    monitoreo_entrada = Thread(target=entrada, name="Entrada")
    
    monitoreo_salida = Thread(target=salida, name="Salida") """
    
    
    """ monitoreo_cpu.start()
    monitoreo_ram.start()
    monitoreo_entrada.start()
    monitoreo_salida.start()
    
    
    monitoreo_ram.join()
    monitoreo_entrada.join()
    monitoreo_salida.join() """
    
    monitoreo_cpu.start()
    monitoreo_cpu.join()
    
    """ monitoreo_ram.start()
    monitoreo_ram.join()
    
    monitoreo_entrada.start()
    monitoreo_entrada.join()
    
    monitoreo_salida.start()
    monitoreo_salida.join() """
    
    limpiar_pantalla()
    print("Umbrale sobrepasados...")
    send_alert_attached("Sobrepasa el umbral")
    print("\nEnviando correos...")
    pausar()
    
    
    
def cpu():
    ultima_actualizacion = rrdtool.lastupdate(rrdpath + "trend.rrd")
    timestamp=ultima_actualizacion['date'].timestamp()
    dato=ultima_actualizacion['ds']["CPUload"]
    
    while 1:  
        if dato > 25:
            grafica_cpu(int(timestamp))
            break
            
        """ elif dato > 50:
            grafica_cpu(int(timestamp))
            
            break
            
        elif dato > 75:
            grafica_cpu(int(timestamp))
            
            break """
        
        ultima_actualizacion = rrdtool.lastupdate(rrdpath + "trend.rrd")
        timestamp=ultima_actualizacion['date'].timestamp()
        dato=ultima_actualizacion['ds']["CPUload"]
        limpiar_pantalla()
        print("Esperando carga en CPU: " + str(dato))
        

def ram():
    ultima_actualizacion = rrdtool.lastupdate(rrdpath + "trend.rrd")
    timestamp=ultima_actualizacion['date'].timestamp()
    dato=ultima_actualizacion['ds']["RAMload"]
    
    while 1:
        if dato > 25:
            graficar_ram(int(timestamp))
            """ send_alert_attached("Sobrepasa el umbral 1") """
            break
            
        elif dato > 50:
            graficar_ram(int(timestamp))
            """ send_alert_attached("Sobrepasa el umbral 2") """
            break
            
        elif dato > 75:
            graficar_ram(int(timestamp))
            """ send_alert_attached("Sobrepasa el umbral 3") """
            break
        
        else:
            ultima_actualizacion = rrdtool.lastupdate(rrdpath + "trend.rrd")
            timestamp=ultima_actualizacion['date'].timestamp()
            dato=ultima_actualizacion['ds']["RAMload"]
            limpiar_pantalla()
            print("Esperando carga en RAM: " + str(dato))
            
        
        
def entrada():
    ultima_actualizacion = rrdtool.lastupdate(rrdpath + "trend.rrd")
    timestamp=ultima_actualizacion['date'].timestamp()
    dato=ultima_actualizacion['ds']["InOct"]
    
    while 1:
        if dato > 1500:
            graficar_entrada(int(timestamp))
            """ send_alert_attached("Sobrepasa el umbral 1") """
            break
            
        elif dato > 2500:
            graficar_entrada(int(timestamp))
            """ send_alert_attached("Sobrepasa el umbral 2") """
            break
            
        elif dato > 4000:
            graficar_entrada(int(timestamp))
            """ send_alert_attached("Sobrepasa el umbral 3") """
            break
        
        else:
            ultima_actualizacion = rrdtool.lastupdate(rrdpath + "trend.rrd")
            timestamp=ultima_actualizacion['date'].timestamp()
            dato=ultima_actualizacion['ds']["InOct"]    
            limpiar_pantalla()
            print("Esperando carga en Entrada: " + str(dato))
        
        
def salida():
    ultima_actualizacion = rrdtool.lastupdate(rrdpath + "trend.rrd")
    timestamp=ultima_actualizacion['date'].timestamp()
    dato=ultima_actualizacion['ds']["InOct"]
    
    while 1:
        if dato > 1500:
            graficar_salida(int(timestamp))
            """ send_alert_attached("Sobrepasa el umbral 1") """
            break
            
        elif dato > 2500:
            graficar_salida(int(timestamp))
            """ send_alert_attached("Sobrepasa el umbral 2") """
            break
            
        elif dato > 4000:
            graficar_salida(int(timestamp))
            """ send_alert_attached("Sobrepasa el umbral 3") """
            break
        
        else:
            ultima_actualizacion = rrdtool.lastupdate(rrdpath + "trend.rrd")
            timestamp=ultima_actualizacion['date'].timestamp()
            dato=ultima_actualizacion['ds']["InOct"]  
            limpiar_pantalla()
            print("Esperando carga en Salida: " + str(dato))

""" Programa Principal """
agentes = []

opcion = desplegar_menu()

while opcion != 5:
    if opcion == 1:
        """ Generamos un nuevo agente """
        crear_agente(agentes)

    elif opcion == 2:
        """ Modificamos los datos de un agente """
        modificar_agente(agentes)

    elif opcion == 3:
        """ Eliminamos un agente, dependiendo su Hostname """
        buscar_hostname(agentes)

    elif opcion == 4:
        """ Monitorizamos el agente agregado """
        monitorizar()
        """ generar_reporte(agentes) """

    opcion = desplegar_menu()

print("\nAdios!")
pausar()
borrar_txt()
limpiar_pantalla()