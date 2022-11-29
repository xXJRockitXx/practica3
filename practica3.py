#!/usr/bin/python3
import os
import rrdtool
import time
from fpdf import FPDF
from base64 import decode
from datetime import datetime
from pysnmp.hlapi import *

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

    def obtener_ubicacion(self):
        """ Hacemos una consulta para obtener ubicacion """
        consulta = consultaSNMP(self.comunidad, self.hostname, "1.3.6.1.2.1.1.6.0")
        return "\nUbicacion: " + consulta

    def obtener_interfaces(self):
        """ Hacemos una consulta para obtener el número de interfaces
        y por cada interfaz, mostrar su estado administratico """
        consulta = consultaSNMP(self.comunidad, self.hostname, "1.3.6.1.2.1.2.1.0")
        return consulta

    def obtener_desc(self, oid):
        """ Hacemos una consulta para una descripción de la
        interfaz """
        consulta = consultaSNMP(self.comunidad, self.hostname, oid)

        if (self.win):
            consulta = consulta[2:]
            consulta = bytes.fromhex(consulta).decode("ASCII")
        return consulta

    def obtener_status(self, oid):
        """ Hacemos una consulta para obtener el status de las
        interfaces """
        consulta = consultaSNMP(self.comunidad, self.hostname, oid)
        return consulta

    def consultas_agente(self):
        consultasTxt = open("consultas.txt", "w")

        insertar_txt(consultasTxt, "version: 1")
        insertar_txt(consultasTxt, "\ndevice: server1")
        insertar_txt(consultasTxt, "\ndescripcion: Accouting Server 1")
        insertar_txt(consultasTxt, "\ndate: 2022-11-09")
        insertar_txt(consultasTxt, "\ndefault protocol: Radius")
        
        insertar_txt(consultasTxt, "\nradte: 2022-11-08")
        insertar_txt(consultasTxt, "\n#NAS-Ip address:")
        insertar_txt(consultasTxt, "\n4:8.40.1.27")
        insertar_txt(consultasTxt, "\n#NAS-Port-Type")
        insertar_txt(consultasTxt, "\n5:61:2")
        insertar_txt(consultasTxt, "\n#NAS-User-name")
        insertar_txt(consultasTxt, self.obtener_contacto())
        insertar_txt(consultasTxt, "\n#Acct-Status-Type:40:1")
        insertar_txt(consultasTxt, "\n#Acct-Delay-Time:")
        insertar_txt(consultasTxt, "\n" + consultaSNMP(self.comunidad, self.hostname, "1.3.6.1.2.1.4.2.0"))
        insertar_txt(consultasTxt, "\n#Acct-Input-Octets:")
        insertar_txt(consultasTxt, "\n" + consultaSNMP(self.comunidad, self.hostname, "1.3.6.1.2.1.2.2.1.10.1"))
        insertar_txt(consultasTxt, "\n#Acct-Output-Octets:")
        insertar_txt(consultasTxt, "\n" + consultaSNMP(self.comunidad, self.hostname, "1.3.6.1.2.1.2.2.1.16.1"))        
        insertar_txt(consultasTxt, "\n#Acct-Session-Id:")
        insertar_txt(consultasTxt, "\n#44:2")

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
    print("Práctica 1 - Adquisición de Información")
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
    pdf.titulos("Practica 2", 0.0, 10.0)
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
    

def generar_graficas(epochInicio, epochFinal):
    """ Generamos las 5 graficas corresponsientes a mi bloque """
    
    """ Graficamos Paquetes multicast que ha enviado la interfaz de la interfaz de red de un agente """
    graficar(
        "Paquetes multicast enviados", "multicast", "Paquetes", 
        "Paquetes multicast que ha enviado la \n interfaz de red de un agente",
        "multiCastSalida", "maxPaq", "#FFC300", "Paquetes enviados", epochInicio, epochFinal)

    """ Graficamos Paquetes IP que los protocolos locales (incluyendo ICMP) suministraron a IP en las 
    solicitudes de transmisión. """
    graficar("Paquetes IP enviados", "paquetesIp", "Paquetes IP", 
            "Paquetes IP que los protocolos locales \n suministraron a IP en la transmisión",
            "paquetesIpSalida", "maxPaq", "#2471a3", "Paquetes enviados", epochInicio, epochFinal)

    """ Graficamos Mensajes ICMP que ha recibido el agente. """
    graficar("Mensajes ICMP recibidos", "icmp", "Mensajes", 
            "Mensajes ICMP que ha recibido \n el agente",
            "icmpEntrada", "maxMen", "#a93226", "Mensajes enviados", epochInicio, epochFinal)

    """ Graficamos Segmentos retransmitidos; es decir, el número de segmentos TCP transmitidos que 
    contienen uno o más octetos transmitidos previamente """
    graficar("Segmentos retransmitidos", "segmentos", "Segmentos", 
            "Segmentos TCP transmitidos que contienen \n uno o más octetos transmitidos previamente",
            "segmentosSalida", "maxSeg", "#6c3483", "Segmentos retransmitidos", epochInicio, epochFinal)

    """ Graficamos Datagramas enviados por el dispositivo """
    graficar("Datagramas enviados", "datagramas", "Datagramas", 
            "Datagramas que ha enviado el\n dispositivo",
            "datagramasSalida", "maxDat", "#2471a3", "Datagramas enviados", epochInicio, epochFinal)


def solicitar_fecha(clave):
    """ Solicitamos la fecha y hora al usuario, luego la convertimos a epoch """
    limpiar_pantalla()
    print("Ingresa la fecha y hora para el reporte (Y/m/d H:M:S)\n")
    
    if (clave == 1):
        print("FECHA INICIAL")
    else:
        print("FECHA FINAL")
    
    fecha = input("Fecha: ")
    epoch = int(datetime.strptime(fecha, "%Y/%m/%d %H:%M:%S").timestamp())
    pausar()
    return epoch

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
        """ Generamos un reporte en PDF """
        epochInicio = solicitar_fecha(1)
        epochFinal = solicitar_fecha(0)
        generar_graficas(epochInicio, epochFinal)
        generar_reporte(agentes)

    opcion = desplegar_menu()

print("\nAdios!")
pausar()
borrar_txt()
limpiar_pantalla()