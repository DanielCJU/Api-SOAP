"""
Titulo software: API AdmisionUTEM
Fecha de Entrega:20-06-2020
Entrega a: Profesor Sebastian Salazar (Ramo Computacion Paralela y Distribuida; UTEM)
Desarrolladores:
    -Ricardo Aliste G.
    -Daniel Cajas
    -Rodrigo Carmona R.
    
Resumen:
API SOAP desarrollada en Python; esta API recibe un listado CSV de, como minimo, 2200 estudiantes (estructurado mediante los datos: RUT;PUNTAJES, siendo
PUNTAJES los puntajes que obtuvieron de NEM, RANKING, PSU lENGUAJE, PSU MATEMATICAS, PSU CIENCIAS, PSU HISTORIA) en BASE64, el MIME type del mismo,y el 
nombre del archivo .csv original.
La API se encarga de ordenar a los mejores estudiantes para cada carrera, en funcion de su puntaje ponderado que corresponde a dicha carrera. Una vez
hecho ese ordenamiento, estos alumnos son registrados en un archivo excel, en el cual cada grupo de alumnos se encuentra en una hoja, la cual corresponde
a la de su carrera.
Este excel es posteriormente encodeado en BASE64, y es devuelto al clinete, junto con el tipo mime correspondiente a un tipo excel, y el nombre de este
mismo.
* Se puede encontrar mas informacion en la carpeta "Material Adicional" del repositorio *
"""
#########################################################      Librerias y Herramientas Importadas      #########################################################
import logging ###Libreria para el sistema
from itertools import cycle

logging.basicConfig(level=logging.DEBUG)

### Sector por libreria Spyne; libreria que permite la conexion de tipo SOAP
from spyne import Application, rpc, ServiceBase, Integer, Unicode
from spyne import Iterable
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.server.wsgi import WsgiApplication
from spyne.protocol.soap import Soap11
from spyne.model.primitive import String

### Sector de librerias importadas por requerimientos
from openpyxl import Workbook ###Libreria para manejo de archivos excel
import base64                 ###Libreria para trabajar BASE64
from mimetypes import guess_type, guess_extension
import re

############################################################      Funciones Externas Utilizadas      ############################################################
def mayor(persona):
    mayor=0
    pos_mayor=0
    for i in range(2,len(persona), 2):
        if(persona[i]>mayor):
            mayor=persona[i]
            pos_mayor=persona[i-1]
    return pos_mayor

def ordenar(carrera, lugar): ###Funcion encargada de ordenar el listado de alumnos de una carrera; utiliza el metodo Quicksort; el parametro que recive es una lista
    tope=len(carrera)
    izquierda=[]
    derecha=[]
    centro=[]
    if(tope>1): ###Corrobora caso en el que solo ahi un elemento; en caso de tener mas de 1 elemento
        pivote=carrera[0][lugar] ###Define el pivote para separar en elementos mayores, menores o iguales a este
        for i in carrera:
            if(i[lugar]>pivote):    ###Si es mayor, va a una lista llamada "Izquierda"
                izquierda.append(i)
            elif(i[lugar]==pivote): ###Si es igual, va a una lista llamada "Centro"
                centro.append(i)
            elif(i[lugar]<pivote):  ###Si es menor, va a una lista llamada "Derecha"
                derecha.append(i)
        return ordenar(izquierda, lugar)+centro+ordenar(derecha, lugar) ###Finalmente, regresa la union de las 3 listas, pero aplicandole esta misma funcion a izquierda y derecha
    else:
        return carrera ###En el caso de solo ser 1 elemento, se devuelve directamente el arreglo, ya que no ahi nada que ordenar

def almacenar(carreras, datos, max_ing, expulsados, lugar): ###Funcion que realiza el guardado de los estudiantes en las listas correspondientes; recibe como parametros, una lista, un par de datos [RUT, PUNTAJE] y el rango maximo de almacenaje
    n=len(carreras)
    inicio=0
    if(n==max_ing): ###En funcion de la cantidad de elementos en la lista, es su funcionamiento, en el caso de que se encuentre a tope la lista
        if(datos[lugar]<carreras[max_ing-1][lugar]):
            expulsados.append(datos)
            return carreras
        if(max_ing==35):
            if(datos[lugar]>carreras[7][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[7][lugar] and datos[lugar]>carreras[14][lugar]):
                inicio=7
            elif(datos[lugar]<=carreras[14][lugar] and datos[lugar]>carreras[21][lugar]):
                inicio=7*2
            elif(datos[lugar]<=carreras[21][lugar] and datos[lugar]>carreras[28][lugar]):
                inicio=7*3
            elif(datos[lugar]<=carreras[28][lugar] and datos[lugar]>=carreras[34][lugar]):
                inicio=7*4
        elif(max_ing==80):
            if(datos[lugar]>carreras[20][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[20][lugar] and datos[lugar]>carreras[40][lugar]):
                inicio=20
            elif(datos[lugar]<=carreras[40][lugar] and datos[lugar]>carreras[60][lugar]):
                inicio=20*2
            elif(datos[lugar]<=carreras[60][lugar] and datos[lugar]>=carreras[80][lugar]):
                inicio=20*3
        elif(max_ing==125):
            if(datos[lugar]>carreras[25][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[25][lugar] and datos[lugar]>carreras[50][lugar]):
                inicio=25
            elif(datos[lugar]<=carreras[50][lugar] and datos[lugar]>carreras[75][lugar]):
                inicio=25*2
            elif(datos[lugar]<=carreras[75][lugar] and datos[lugar]>carreras[100][lugar]):
                inicio=25*3
            elif(datos[lugar]<=carreras[100][lugar] and datos[lugar]>=carreras[124][lugar]):
                inicio=25*4
        elif(max_ing==30):
            if(datos[lugar]>carreras[6][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[6][lugar] and datos[lugar]>carreras[12][lugar]):
                inicio=6
            elif(datos[lugar]<=carreras[12][lugar] and datos[lugar]>carreras[18][lugar]):
                inicio=6*2
            elif(datos[lugar]<=carreras[18][lugar] and datos[lugar]>carreras[24][lugar]):
                inicio=6*3
            elif(datos[lugar]<=carreras[24][lugar] and datos[lugar]>=carreras[29][lugar]):
                inicio=6*4
        elif(max_ing==90):
            if(datos[lugar]>carreras[15][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[15][lugar] and datos[lugar]>carreras[30][lugar]):
                inicio=15
            elif(datos[lugar]<=carreras[30][lugar] and datos[lugar]>carreras[45][lugar]):
                inicio=15*2
            elif(datos[lugar]<=carreras[45][lugar] and datos[lugar]>carreras[60][lugar]):
                inicio=15*3
            elif(datos[lugar]<=carreras[60][lugar] and datos[lugar]>carreras[75][lugar]):
                inicio=15*4
            elif(datos[lugar]<=carreras[75][lugar] and datos[lugar]>=carreras[89][lugar]):
                inicio=15*5
        elif(max_ing==25):
            if(datos[lugar]>carreras[5][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[5][lugar] and datos[lugar]>carreras[10][lugar]):
                inicio=5
            elif(datos[lugar]<=carreras[10][lugar] and datos[lugar]>carreras[15][lugar]):
                inicio=5*2
            elif(datos[lugar]<=carreras[15][lugar] and datos[lugar]>carreras[20][lugar]):
                inicio=5*3
            elif(datos[lugar]<=carreras[20][lugar] and datos[lugar]>=carreras[24][lugar]):
                inicio=5*4
        elif(max_ing==100):
            if(datos[lugar]>carreras[20][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[20][lugar] and datos[lugar]>carreras[40][lugar]):
                inicio=20
            elif(datos[lugar]<=carreras[40][lugar] and datos[lugar]>carreras[60][lugar]):
                inicio=20*2
            elif(datos[lugar]<=carreras[60][lugar] and datos[lugar]>carreras[80][lugar]):
                inicio=20*3
            elif(datos[lugar]<=carreras[80][lugar] and datos[lugar]>=carreras[99][lugar]):
                inicio=20*4
        elif(max_ing==60):
            if(datos[lugar]>carreras[12][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[12][lugar] and datos[lugar]>carreras[24][lugar]):
                inicio=12
            elif(datos[lugar]<=carreras[24][lugar] and datos[lugar]>carreras[36][lugar]):
                inicio=12*2
            elif(datos[lugar]<=carreras[36][lugar] and datos[lugar]>carreras[48][lugar]):
                inicio=12*3
            elif(datos[lugar]<=carreras[48][lugar] and datos[lugar]>=carreras[59][lugar]):
                inicio=12*4
        elif(max_ing==40):
            if(datos[lugar]>carreras[8][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[8][lugar] and datos[lugar]>carreras[16][lugar]):
                inicio=8
            elif(datos[lugar]<=carreras[16][lugar] and datos[lugar]>carreras[24][lugar]):
                inicio=8*2
            elif(datos[lugar]<=carreras[24][lugar] and datos[lugar]>carreras[32][lugar]):
                inicio=8*3
            elif(datos[lugar]<=carreras[32][lugar] and datos[lugar]>=carreras[39][lugar]):
                inicio=8*4
        elif(max_ing==65):
            if(datos[lugar]>carreras[13][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[13][lugar] and datos[lugar]>carreras[26][lugar]):
                inicio=13
            elif(datos[lugar]<=carreras[26][lugar] and datos[lugar]>carreras[39][lugar]):
                inicio=13*2
            elif(datos[lugar]<=carreras[39][lugar] and datos[lugar]>carreras[52][lugar]):
                inicio=13*3
            elif(datos[lugar]<=carreras[52][lugar] and datos[lugar]>=carreras[64][lugar]):
                inicio=13*4
        elif(max_ing==95):
            if(datos[lugar]>carreras[19][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[19][lugar] and datos[lugar]>carreras[38][lugar]):
                inicio=19
            elif(datos[lugar]<=carreras[38][lugar] and datos[lugar]>carreras[57][lugar]):
                inicio=19*2
            elif(datos[lugar]<=carreras[57][lugar] and datos[lugar]>carreras[76][lugar]):
                inicio=19*3
            elif(datos[lugar]<=carreras[76][lugar] and datos[lugar]>=carreras[94][lugar]):
                inicio=19*4
        elif(max_ing==130):
            if(datos[lugar]>carreras[26][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[26][lugar] and datos[lugar]>carreras[52][lugar]):
                inicio=26
            elif(datos[lugar]<=carreras[52][lugar] and datos[lugar]>carreras[78][lugar]):
                inicio=26*2
            elif(datos[lugar]<=carreras[78][lugar] and datos[lugar]>carreras[104][lugar]):
                inicio=26*3
            elif(datos[lugar]<=carreras[104][lugar] and datos[lugar]>=carreras[129][lugar]):
                inicio=26*4
        elif(max_ing==200):
            if(datos[lugar]>carreras[20][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[20][lugar] and datos[lugar]>carreras[40][lugar]):
                inicio=20
            elif(datos[lugar]<=carreras[40][lugar] and datos[lugar]>carreras[60][lugar]):
                inicio=20*2
            elif(datos[lugar]<=carreras[60][lugar] and datos[lugar]>carreras[80][lugar]):
                inicio=20*3
            elif(datos[lugar]<=carreras[80][lugar] and datos[lugar]>carreras[100][lugar]):
                inicio=20*4
            elif(datos[lugar]<=carreras[100][lugar] and datos[lugar]>carreras[120][lugar]):
                inicio=20*5
            elif(datos[lugar]<=carreras[120][lugar] and datos[lugar]>carreras[140][lugar]):
                inicio=20*6
            elif(datos[lugar]<=carreras[140][lugar] and datos[lugar]>carreras[160][lugar]):
                inicio=20*7
            elif(datos[lugar]<=carreras[160][lugar] and datos[lugar]>carreras[180][lugar]):
                inicio=20*8
            elif(datos[lugar]<=carreras[180][lugar] and datos[lugar]>carreras[199][lugar]):
                inicio=20*9
        elif(max_ing==105):
            if(datos[lugar]>carreras[15][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[15][lugar] and datos[lugar]>carreras[30][lugar]):
                inicio=15
            elif(datos[lugar]<=carreras[30][lugar] and datos[lugar]>carreras[45][lugar]):
                inicio=15*2
            elif(datos[lugar]<=carreras[45][lugar] and datos[lugar]>carreras[60][lugar]):
                inicio=15*3
            elif(datos[lugar]<=carreras[60][lugar] and datos[lugar]>carreras[75][lugar]):
                inicio=15*4
            elif(datos[lugar]<=carreras[75][lugar] and datos[lugar]>carreras[90][lugar]):
                inicio=15*5
            elif(datos[lugar]<=carreras[90][lugar] and datos[lugar]>carreras[104][lugar]):
                inicio=15*6
        for posicion in range (inicio, max_ing): ###En caso de ser mas grande que el mas pequeño, se procedera a identificar mediante un for...
            if(carreras[posicion][1]<=datos[1]):
                expulsados.append(carreras[max_ing-1])
                carreras=carreras[0:(posicion)]+[datos]+carreras[(posicion):(max_ing-1)]
                return carreras

    elif(n>=0 and n<(max_ing-1)): ###En caso de que aun no se llegue al tope, simplemente se iran agregando los valores a la lista
        carreras.append(datos)
        return carreras
    elif(n==(max_ing-1)): ###Y, en el caso de que tras ingresar este valor, se alcance el tope, tras ingresarlo, se realizara un ordenamiento descendente de la lista. 
        carreras.append(datos)
        return ordenar(carreras, lugar)

def almacenar_cambiante(carreras, datos, max_ing, expulsados, lugar): ###Funcion que realiza el guardado de los estudiantes en las listas correspondientes; recibe como parametros, una lista, un par de datos [RUT, PUNTAJE] y el rango maximo de almacenaje
    n=len(carreras)
    inicio=0
    if(n==max_ing): ###En funcion de la cantidad de elementos en la lista, es su funcionamiento, en el caso de que se encuentre a tope la lista
        if(datos[lugar]<carreras[max_ing-1][lugar]):
            return False
        if(max_ing==35):
            if(datos[lugar]>carreras[7][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[7][lugar] and datos[lugar]>carreras[14][lugar]):
                inicio=7
            elif(datos[lugar]<=carreras[14][lugar] and datos[lugar]>carreras[21][lugar]):
                inicio=7*2
            elif(datos[lugar]<=carreras[21][lugar] and datos[lugar]>carreras[28][lugar]):
                inicio=7*3
            elif(datos[lugar]<=carreras[28][lugar] and datos[lugar]>=carreras[34][lugar]):
                inicio=7*4
        elif(max_ing==80):
            if(datos[lugar]>carreras[20][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[20][lugar] and datos[lugar]>carreras[40][lugar]):
                inicio=20
            elif(datos[lugar]<=carreras[40][lugar] and datos[lugar]>carreras[60][lugar]):
                inicio=20*2
            elif(datos[lugar]<=carreras[60][lugar] and datos[lugar]>=carreras[80][lugar]):
                inicio=20*3
        elif(max_ing==125):
            if(datos[lugar]>carreras[25][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[25][lugar] and datos[lugar]>carreras[50][lugar]):
                inicio=25
            elif(datos[lugar]<=carreras[50][lugar] and datos[lugar]>carreras[75][lugar]):
                inicio=25*2
            elif(datos[lugar]<=carreras[75][lugar] and datos[lugar]>carreras[100][lugar]):
                inicio=25*3
            elif(datos[lugar]<=carreras[100][lugar] and datos[lugar]>=carreras[124][lugar]):
                inicio=25*4
        elif(max_ing==30):
            if(datos[lugar]>carreras[6][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[6][lugar] and datos[lugar]>carreras[12][lugar]):
                inicio=6
            elif(datos[lugar]<=carreras[12][lugar] and datos[lugar]>carreras[18][lugar]):
                inicio=6*2
            elif(datos[lugar]<=carreras[18][lugar] and datos[lugar]>carreras[24][lugar]):
                inicio=6*3
            elif(datos[lugar]<=carreras[24][lugar] and datos[lugar]>=carreras[29][lugar]):
                inicio=6*4
        elif(max_ing==90):
            if(datos[lugar]>carreras[15][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[15][lugar] and datos[lugar]>carreras[30][lugar]):
                inicio=15
            elif(datos[lugar]<=carreras[30][lugar] and datos[lugar]>carreras[45][lugar]):
                inicio=15*2
            elif(datos[lugar]<=carreras[45][lugar] and datos[lugar]>carreras[60][lugar]):
                inicio=15*3
            elif(datos[lugar]<=carreras[60][lugar] and datos[lugar]>carreras[75][lugar]):
                inicio=15*4
            elif(datos[lugar]<=carreras[75][lugar] and datos[lugar]>=carreras[89][lugar]):
                inicio=15*5
        elif(max_ing==25):
            if(datos[lugar]>carreras[5][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[5][lugar] and datos[lugar]>carreras[10][lugar]):
                inicio=5
            elif(datos[lugar]<=carreras[10][lugar] and datos[lugar]>carreras[15][lugar]):
                inicio=5*2
            elif(datos[lugar]<=carreras[15][lugar] and datos[lugar]>carreras[20][lugar]):
                inicio=5*3
            elif(datos[lugar]<=carreras[20][lugar] and datos[lugar]>=carreras[24][lugar]):
                inicio=5*4
        elif(max_ing==100):
            if(datos[lugar]>carreras[20][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[20][lugar] and datos[lugar]>carreras[40][lugar]):
                inicio=20
            elif(datos[lugar]<=carreras[40][lugar] and datos[lugar]>carreras[60][lugar]):
                inicio=20*2
            elif(datos[lugar]<=carreras[60][lugar] and datos[lugar]>carreras[80][lugar]):
                inicio=20*3
            elif(datos[lugar]<=carreras[80][lugar] and datos[lugar]>=carreras[99][lugar]):
                inicio=20*4
        elif(max_ing==60):
            if(datos[lugar]>carreras[12][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[12][lugar] and datos[lugar]>carreras[24][lugar]):
                inicio=12
            elif(datos[lugar]<=carreras[24][lugar] and datos[lugar]>carreras[36][lugar]):
                inicio=12*2
            elif(datos[lugar]<=carreras[36][lugar] and datos[lugar]>carreras[48][lugar]):
                inicio=12*3
            elif(datos[lugar]<=carreras[48][lugar] and datos[lugar]>=carreras[59][lugar]):
                inicio=12*4
        elif(max_ing==40):
            if(datos[lugar]>carreras[8][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[8][lugar] and datos[lugar]>carreras[16][lugar]):
                inicio=8
            elif(datos[lugar]<=carreras[16][lugar] and datos[lugar]>carreras[24][lugar]):
                inicio=8*2
            elif(datos[lugar]<=carreras[24][lugar] and datos[lugar]>carreras[32][lugar]):
                inicio=8*3
            elif(datos[lugar]<=carreras[32][lugar] and datos[lugar]>=carreras[39][lugar]):
                inicio=8*4
        elif(max_ing==65):
            if(datos[lugar]>carreras[13][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[13][lugar] and datos[lugar]>carreras[26][lugar]):
                inicio=13
            elif(datos[lugar]<=carreras[26][lugar] and datos[lugar]>carreras[39][lugar]):
                inicio=13*2
            elif(datos[lugar]<=carreras[39][lugar] and datos[lugar]>carreras[52][lugar]):
                inicio=13*3
            elif(datos[lugar]<=carreras[52][lugar] and datos[lugar]>=carreras[64][lugar]):
                inicio=13*4
        elif(max_ing==95):
            if(datos[lugar]>carreras[19][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[19][lugar] and datos[lugar]>carreras[38][lugar]):
                inicio=19
            elif(datos[lugar]<=carreras[38][lugar] and datos[lugar]>carreras[57][lugar]):
                inicio=19*2
            elif(datos[lugar]<=carreras[57][lugar] and datos[lugar]>carreras[76][lugar]):
                inicio=19*3
            elif(datos[lugar]<=carreras[76][lugar] and datos[lugar]>=carreras[94][lugar]):
                inicio=19*4
        elif(max_ing==130):
            if(datos[lugar]>carreras[26][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[26][lugar] and datos[lugar]>carreras[52][lugar]):
                inicio=26
            elif(datos[lugar]<=carreras[52][lugar] and datos[lugar]>carreras[78][lugar]):
                inicio=26*2
            elif(datos[lugar]<=carreras[78][lugar] and datos[lugar]>carreras[104][lugar]):
                inicio=26*3
            elif(datos[lugar]<=carreras[104][lugar] and datos[lugar]>=carreras[129][lugar]):
                inicio=26*4
        elif(max_ing==200):
            if(datos[lugar]>carreras[20][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[20][lugar] and datos[lugar]>carreras[40][lugar]):
                inicio=20
            elif(datos[lugar]<=carreras[40][lugar] and datos[lugar]>carreras[60][lugar]):
                inicio=20*2
            elif(datos[lugar]<=carreras[60][lugar] and datos[lugar]>carreras[80][lugar]):
                inicio=20*3
            elif(datos[lugar]<=carreras[80][lugar] and datos[lugar]>carreras[100][lugar]):
                inicio=20*4
            elif(datos[lugar]<=carreras[100][lugar] and datos[lugar]>carreras[120][lugar]):
                inicio=20*5
            elif(datos[lugar]<=carreras[120][lugar] and datos[lugar]>carreras[140][lugar]):
                inicio=20*6
            elif(datos[lugar]<=carreras[140][lugar] and datos[lugar]>carreras[160][lugar]):
                inicio=20*7
            elif(datos[lugar]<=carreras[160][lugar] and datos[lugar]>carreras[180][lugar]):
                inicio=20*8
            elif(datos[lugar]<=carreras[180][lugar] and datos[lugar]>carreras[199][lugar]):
                inicio=20*9
        elif(max_ing==105):
            if(datos[lugar]>carreras[15][lugar]):
                inicio=0
            elif(datos[lugar]<=carreras[15][lugar] and datos[lugar]>carreras[30][lugar]):
                inicio=15
            elif(datos[lugar]<=carreras[30][lugar] and datos[lugar]>carreras[45][lugar]):
                inicio=15*2
            elif(datos[lugar]<=carreras[45][lugar] and datos[lugar]>carreras[60][lugar]):
                inicio=15*3
            elif(datos[lugar]<=carreras[60][lugar] and datos[lugar]>carreras[75][lugar]):
                inicio=15*4
            elif(datos[lugar]<=carreras[75][lugar] and datos[lugar]>carreras[90][lugar]):
                inicio=15*5
            elif(datos[lugar]<=carreras[90][lugar] and datos[lugar]>carreras[104][lugar]):
                inicio=15*6
        for posicion in range(inicio, max_ing): ###En caso de ser mas grande que el mas pequeño, se procedera a identificar mediante un for...
            if(carreras[posicion][1]<=datos[1]):
                expulsados.append(carreras[max_ing-1])
                carreras=carreras[0:(posicion)]+[datos]+carreras[(posicion):(max_ing-1)]
                return True
    elif(n>=0 and n<(max_ing-1)): ###En caso de que aun no se llegue al tope, simplemente se iran agregando los valores a la lista
        carreras.append(datos)
        return True
    elif(n==(max_ing-1)): ###Y, en el caso de que tras ingresar este valor, se alcance el tope, tras ingresarlo, se realizara un ordenamiento descendente de la lista. 
        carreras.append(datos)
        carreras=ordenar(carreras, lugar)
        return True

def entregarCarrera(indice): ###Funcion encargada de devolver el codigo de cada carrera, en funcion a un parametro indice que recibe;
    if(indice==0):
        return "21089" ###Administracion Publica
    elif(indice==1):
        return "21002" ###Bibliotecología y Documentación
    elif(indice==2):
        return "21012" ###Contador Público y Auditor
    elif(indice==3):
        return "21048" ###Ingeniería Comercial
    elif(indice==4):
        return "21015" ###Ingeniería en Administración Agroindustrial
    elif(indice==5):
        return "21081" ###Ingeniería en Comercio Internacional
    elif(indice==6):
        return "21082" ###Ingeniería en Gestión Turística
    elif(indice==7):
        return "21047" ###Arquitectura
    elif(indice==8):
        return "21074" ###Ingeniería Civil en Obras Civiles
    elif(indice==9):
        return "21032" ###Ingeniería en Construcción
    elif(indice==10):
        return "21087" ###Ingeniería Civil en Prevención de Riesgos y Medioambiente
    elif(indice==11):
        return "21073" ###Ingeniería en Biotecnología
    elif(indice==12):
        return "21039" ###Ingeniería en Industria Alimentaria
    elif(indice==13):
        return "21080" ###Ingeniería en Química
    elif(indice==14):
        return "21083" ###Química Industrial
    elif(indice==15):
        return "21024" ###Diseño en Comunicación Visual
    elif(indice==16):
        return "21023" ###Diseño Industrial
    elif(indice==17):
        return "21043" ###Trabajo Social
    elif(indice==18):
        return "21046" ###Bachillerato en Ciencias de la Ingeniería
    elif(indice==19):
        return "21071" ###Dibujante Proyectista
    elif(indice==20):
        return "21041" ###Ingeniería Civil en Computación, mención Informática
    elif(indice==21):
        return "21076" ###Ingeniería Civil Industrial
    elif(indice==22):
        return "21049" ###Ingeniería Civil en Ciencia de Datos
    elif(indice==23):
        return "21075" ###Ingeniería Civil Electrónica
    elif(indice==24):
        return "21096" ###Ingeniería Civil en Mecánica
    elif(indice==25):
        return "21031" ###Ingeniería en Geomensura
    elif(indice==26):
        return "21030" ###Ingeniería en Informática
    elif(indice==27):
        return "21045" ###Ingeniería Industrial

def insertar(carreras): ###Funcion encargada de crear y poblar las diversas hojas del excel; Recibe como parametro el listado de listas de las carreras
    excel = Workbook() ###Crea el excel
    for carrera in carreras: ###Luego, por cada carrera...
        indice = carreras.index(carrera) ###...Identifica su codigo...
        hoja = excel.create_sheet(entregarCarrera(indice),indice) ###...Crea una nueva hoja...
        fila = 1
        ###Crea las etiquetas para las columnas de datos
        hoja['A'+str(fila)]='INDICE'
        hoja['B'+str(fila)]='RUT'
        hoja['C'+str(fila)]='PUNTAJE'
        for dato in carrera: ###...Y procede finlamente a registrar a cada estudiante en el excel
            fila+=1
            hoja['A'+str(fila)] = (carrera.index(dato)+1)
            hoja['B'+str(fila)] = dato[0]
            hoja['C'+str(fila)] = dato[1]
    del excel['Sheet'] ###Luego limpia datos
    nombre="Admision UTEM.xlsx"
    excel.save(nombre) ###Y realiza el guardado del excel en la maquina


def extrapolarMime(nombre): ###Funcion para corroborar el tipo mime en base al nombre
    mimetuple=guess_type(nombre) ###Obtiene un listado de tipos mime para el nombre
    if(mimetuple[0]=="application/vnd.ms-excel" and re.search(".csv$" , nombre)): ###En caso de serlo, retornara el tipo mime "text/csv"
        return "text/csv"
    else:
        return mimetuple[0] ###En caso contrario, retornara una distinta

def obtenerMime(stringstream): ###Funcion para corroborar el tipo mime del string en base64
    if(stringstream):
        string = stringstream[0:200]
        stringb = string[0:43]+'='
        if(determinarBase64(stringb)):
            string64 = (base64.b64decode(stringb.encode("utf-8"))).decode("utf-8")
            if(re.search("text\/(\w+)", string64)):                
                if(re.findall("text\/(\w+)", string64)[0]=="csv"):
                    return "text/csv"
            elif(re.search("(.+)\.(\w+)",string64)):                
                lista = (re.findall("(.+)\.(\w+)",string64))
                for caso in lista:
                    for palabra in caso:
                        if(palabra=="csv"):
                            return "text/csv"
                        elif(palabra=="txt"):
                            return "text/plain"
            elif(re.search("data:text\/(\w+)", string64)):
                if(re.findall("data:text\/(\w+)", string64)[0]=="csv"):
                    return "text/csv"
            return "Codificado"
        elif(re.search("text\/(\w+)", string)):
            if(re.findall("text\/(\w+)", string)[0]=="csv"):
                return "text/csv"
        elif(re.search("(.+)\.(\w+)",string)):
            lista = (re.findall("(.+)\.(\w+)",string))
            for caso in lista:
                for palabra in caso:
                    if(palabra=="csv"):
                        return "text/csv"
                    elif(palabra=="txt"):
                        return "text/plain"
        elif(re.search("data:text\/(\w+)", string)):
            if(re.findall("data:text\/(\w+)", string)[0]=="csv"):
                return "text/csv"
        return "Invalid"

def determinarBase64(stringbin): ###Funcion que corrobora que el string recibido esta en base64
    try:
        if isinstance(stringbin, str):
            strbytes = bytes(stringbin, 'ascii')
        elif isinstance(stringbin, bytes):
            strbytes = stringbin
        else:
            raise ValueError("El arumento debe ser un string o un string binario")
        return base64.b64encode(base64.b64decode(strbytes)) == strbytes
    except Exception:
        return False

def corroborarTipoMime(nombre, string, tipoMIME): ###Funcion encargada de corroborar si el tipo mime del string base64, el tipo mime enviado y el del nombre del archivo concuerdan
    mimeString=obtenerMime(string)  ###Confirma tipo mime del string base64
    mimeName=extrapolarMime(nombre) ###Confirma tipo mime del nombre
    if(not mimeName): ###En el caso de que el tipo mime del nombre no sea valido...
        return False
    elif(mimeString=="Invalid"): ###... o en el caso de que no sea un string valido...
        return False
    elif(mimeString=="Codificado" and mimeName==tipoMIME): ###En caso de confirmarse que esta base64, y que el tipo mime es TEXT/CSV, retorna un True
        return True
    elif(not (mimeString==mimeName)): ##... o en el caso de que no uno no sea del tipo mime correspondiente, retornara un False
        return False
    return True

##############################################################      Servicio API desarrollado      ##############################################################
class psuService(ServiceBase):                                    ###Declaracion de clase "psuService" para consumo de la API
    @rpc(Unicode, Unicode, Unicode, _returns = Iterable(Unicode)) ###Decorador para consumo de la API
    def separacion(ctx, nombre_archivo, mime, dato_64):           ###Funcion a consumir, recibe como parametro un ctx (viene por defecto), nombre del archivo enviado en base64, el tipo mime seleccionado del archivo enviado, y el archivo mismo, en base64
        """
        Detalle importante para el profesor: al estar trabajando en soap, y por el mencionado problema de too long 
        por el string base64, es que decidi añadir la siguiente linea, por si es que llegara a ser necesaria
        
        dato_64=open("puntajes-64.txt", "r")
        
        Gracias a que el programa esta elaborado en python, es pisoble hacer algo asi; si desea usar otro archivo en 
        otra ubicacion distinta a la de este codigo python, recordar cambiar lo de *puntajes.csv".
        """
        print("Datos recibidos")
        ###Activacion de variables de apoyo y almacenamiento
        n=[0, 0, 0, 0, 0, 0] ###Contadores para areas con multiples carreras
        i=0
        carreras=[] ###Lista de listas (listado de carreras)
        for i in range(0, 28):
            carreras.append([])

        todos = []  ###Lista de listas (listado de los mejores por area)
        postulantes_anteriores=[]
        postulantes_actuales=[]
        
        mime=mime.lower() ###Se para el tipo mime a minusculas para la comparacion del tipo mime detectado y el tipo mime recibido
        if(corroborarTipoMime(nombre_archivo, dato_64,mime)): ###Comprobacion de que el tipo mime concuerde con el establecido en el nombre y el archivo enviado en base64
            pass
        else: ###En caso de no serlo, entrega una aviso del error y da un ejemplo al usuario; luego termina el proceso
            yield("\nExtension no compatible, asegurese de especificar nombre completo del archivo (incluyendo extension) y el archivo en base64\n\nEjemplo de ingreso\nnombre: 5000.csv  mime:.csv  datos_64: *el string en base 64*")
            return 0
        
        ###Se realiza el cambio la naturaleza del string en base64 a texto plano 
        base64_bytes = dato_64.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode('ascii')
        message=message.split("\n") ###Se realiza separacion de cada linea del texto
        print("Datos corroborados")
        q=0
        ###Ciclo iterativo linea por linea para obtener toda la informacion del documento recibido
        for linea in message: 
            if(len(linea)!=0): ###Condicion para detectar si el arreglo esta vacio (ultima linea), o tienen contenido
                linea=linea.split(";") ###Se realiza la separacion de los valores

                ###Se realiza la conersion de los valores para poder operarlos y registrarlos
                rut=linea[0]
                nem=int(linea[1])
                ranking=int(linea[2])
                lenguaje=int(linea[3])
                matematicas=int(linea[4])
                ciencias=int(linea[5])
                historia=int(linea[6])

                ### Se almacena los puntajes ponderados de cada area (se trabaja con "areas", debido a las carreras de igual ponderacion)
                c1=float(nem*0.15+ranking*0.2+lenguaje*0.3+matematicas*0.25)     ###Carrera 21089
                c2=float(nem*0.2+ranking*0.2+lenguaje*0.4+matematicas*0.1)       ###Carrera 21002
                c3=float(nem*0.2+ranking*0.2+lenguaje*0.3+matematicas*0.15)      ###Carrera 21012
                c4_7=float(nem*0.1+ranking*0.2+lenguaje*0.3+matematicas*0.3)     ###Carreras: 21048-21047
                c8=float(nem*0.15+ranking*0.25+lenguaje*0.2+matematicas*0.2)     ###Carrera 21074
                c9_10=float(nem*0.2+ranking*0.2+lenguaje*0.15+matematicas*0.35)  ###Carreras: 21032-21087
                c11=float(nem*0.15+ranking*0.35+lenguaje*0.2+matematicas*0.2)    ###Carrera 21073
                c12_13=float(nem*0.15+ranking*0.25+lenguaje*0.2+matematicas*0.3) ###Carreras: 21039-21080
                c14_15=float(nem*0.1+ranking*0.25+lenguaje*0.15+matematicas*0.3) ###Carreras: 21083-21024
                c16_17=float(nem*0.1+ranking*0.4+lenguaje*0.3+matematicas*0.1)   ###Carreras: 21023-21043
                c18=float(nem*0.2+ranking*0.3+lenguaje*0.2+matematicas*0.1)      ###Carrera 21046
                c19_28=float(nem*0.1+ranking*0.25+lenguaje*0.2+matematicas*0.35) ###Carreras: 21071-21045
                
                ###Se realiza una comparacion en funcion del puntaje de ciencias e historia; el mayor es agregado al puntaje final
                if(historia>=ciencias): ###En caso de que el puntaje de historia sea mayor que el de ciencias
                    c1=c1+float(historia*0.1)
                    c2=c2+float(historia*0.1)
                    c3=c3+float(historia*0.15)
                    c4_7=c4_7+float(historia*0.1)
                    c8=c8+float(historia*0.2)
                    c9_10=c9_10+float(historia*0.1)
                    c11=c11+float(historia*0.1)
                    c12_13=c12_13+float(historia*0.1)
                    c14_15=c14_15+float(historia*0.2)
                    c16_17=c16_17+float(historia*0.1)
                    c18=c18+float(historia*0.2)
                    c19_28=c19_28+float(historia*0.1)
                else:                    ###En el casocontrario, en el que ciencias es mayor a historia
                    c1=c1+float(ciencias*0.1)
                    c2=c2+float(ciencias*0.1)
                    c3=c3+float(ciencias*0.1)
                    c4_7=c4_7+float(ciencias*0.1)
                    c8=c8+float(ciencias*0.2)
                    c9_10=c9_10+float(ciencias*0.1)
                    c11=c11+float(ciencias*0.1)
                    c12_13=c12_13+float(ciencias*0.1)
                    c14_15=c14_15+float(ciencias*0.2)
                    c16_17=c16_17+float(ciencias*0.1)
                    c18=c18+float(ciencias*0.2)
                    c19_28=c19_28+float(ciencias*0.1)

                ###Ya con todos los puntajes ponderados, estos son almacenados; Este almacenamiento es para crear los grupos con los mejores puntajes para cada area
                ###Estos grupos son de 2100 estudiantes, para evitar caer en el caso de que no sean suficientes estudiantes para cumplir la cuota del documento (2055)
                postulante=[rut,1,c1,2,c2,3,c3,4,c4_7,5,c8,6,c9_10,7,c11,8,c12_13,9,c14_15,10,c16_17,11,c18,12,c19_28]
                lugar=mayor(postulante)
                if(lugar==1):
                    carreras[0]=almacenar(carreras[0], postulante, 35, postulantes_anteriores, lugar*2)
                elif(lugar==2):
                    carreras[1]=almacenar(carreras[1], postulante, 35, postulantes_anteriores, lugar*2)
                elif(lugar==3):
                    carreras[2]=almacenar(carreras[2], postulante, 80, postulantes_anteriores, lugar*2)
                elif(lugar==4):
                    if(len(carreras[3])<22):
                        carreras[3]=almacenar(carreras[3], postulante, 125, postulantes_anteriores, lugar*2)
                    elif(len(carreras[4])<22):
                        carreras[4]=almacenar(carreras[4], postulante, 30, postulantes_anteriores, lugar*2)
                    elif(len(carreras[5])<22):
                        carreras[5]=almacenar(carreras[5], postulante, 90, postulantes_anteriores, lugar*2)
                    else:
                        carreras[6]=almacenar(carreras[6], postulante, 25, postulantes_anteriores, lugar*2)
                elif(lugar==5):
                    carreras[7]=almacenar(carreras[7], postulante, 100, postulantes_anteriores, lugar*2)
                elif(lugar==6):
                    if(len(carreras[8])<22):
                        carreras[8]=almacenar(carreras[8], postulante, 100, postulantes_anteriores, lugar*2)
                    else:
                        carreras[9]=almacenar(carreras[9], postulante, 100, postulantes_anteriores, lugar*2)
                elif(lugar==7):
                    carreras[10]=almacenar(carreras[10], postulante, 30, postulantes_anteriores, lugar*2)
                elif(lugar==8):
                    if(len(carreras[11])<22):
                        carreras[11]=almacenar(carreras[11], postulante, 60, postulantes_anteriores, lugar*2)
                    else:
                        carreras[12]=almacenar(carreras[12], postulante, 30, postulantes_anteriores, lugar*2)
                elif(lugar==9):
                    if(len(carreras[13])<22):
                        carreras[13]=almacenar(carreras[13], postulante, 80, postulantes_anteriores, lugar*2)
                    else:
                        carreras[14]=almacenar(carreras[14], postulante, 40, postulantes_anteriores, lugar*2)
                elif(lugar==10):
                    if(len(carreras[15])<22):
                        carreras[15]=almacenar(carreras[15], postulante, 100, postulantes_anteriores, lugar*2)
                    else:
                        carreras[16]=almacenar(carreras[16], postulante, 65, postulantes_anteriores, lugar*2)
                elif(lugar==11):
                    carreras[17]=almacenar(carreras[17], postulante, 95, postulantes_anteriores, lugar*2)
                elif(lugar==12):
                    if(len(carreras[18])<22):
                        carreras[18]=almacenar(carreras[18], postulante, 25, postulantes_anteriores, lugar*2)
                    elif(len(carreras[19])<22):
                        carreras[19]=almacenar(carreras[19], postulante, 25, postulantes_anteriores, lugar*2)
                    elif(len(carreras[20])<22):
                        carreras[20]=almacenar(carreras[20], postulante, 130, postulantes_anteriores, lugar*2)
                    elif(len(carreras[21])<22):
                        carreras[21]=almacenar(carreras[21], postulante, 200, postulantes_anteriores, lugar*2)
                    elif(len(carreras[22])<22):
                        carreras[22]=almacenar(carreras[22], postulante, 60, postulantes_anteriores, lugar*2)
                    elif(len(carreras[23])<22):
                        carreras[23]=almacenar(carreras[23], postulante, 80, postulantes_anteriores, lugar*2)
                    elif(len(carreras[24])<22):
                        carreras[24]=almacenar(carreras[24], postulante, 90, postulantes_anteriores, lugar*2)
                    elif(len(carreras[25])<22):
                        carreras[25]=almacenar(carreras[25], postulante, 60, postulantes_anteriores, lugar*2)
                    elif(len(carreras[26])<22):
                        carreras[26]=almacenar(carreras[26], postulante, 105, postulantes_anteriores, lugar*2)
                    else:
                        carreras[27]=almacenar(carreras[27], postulante, 60, postulantes_anteriores, lugar*2)
            else: ###Caso de la ultima linea (linea vacia)
                pass
        postulantes_actuales=postulantes_anteriores
        postulantes_anteriores=[]

        print("primera parte completa")
        j=0
        sw=False
        while(len(postulantes_anteriores)!=(5000-2055) or sw==False):
            postulantes_anteriores=postulantes_actuales
            postulantes_actuales=[]
            i=0
            print(len(postulantes_anteriores))
            for postulante in postulantes_anteriores:
                semaforo=almacenar_cambiante(carreras[11], postulante, 60, postulantes_actuales, 8*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[22], postulante, 60, postulantes_actuales, 12*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[20], postulante, 60, postulantes_actuales, 12*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[7], postulante, 100, postulantes_actuales, 5*2)
                    i+=1
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[0], postulante, 35, postulantes_actuales, 1*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[17], postulante, 95, postulantes_actuales, 11*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[26], postulante, 105, postulantes_actuales, 12*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[24], postulante, 60, postulantes_actuales, 12*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[18], postulante, 25, postulantes_actuales, 12*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[21], postulante, 60, postulantes_actuales, 12*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[23], postulante, 60, postulantes_actuales, 12*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[3], postulante, 125, postulantes_actuales, 4*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[19], postulante, 25, postulantes_actuales, 12*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[25], postulante, 60, postulantes_actuales, 12*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[9], postulante, 100, postulantes_actuales, 6*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[27], postulante, 60, postulantes_actuales, 12*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[8], postulante, 100, postulantes_actuales, 6*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[14], postulante, 40, postulantes_actuales, 9*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[12], postulante, 30, postulantes_actuales, 8*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[10], postulante, 30, postulantes_actuales, 7*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[4], postulante, 30, postulantes_actuales, 4*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[5], postulante, 90, postulantes_actuales, 4*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[1], postulante, 35, postulantes_actuales, 2*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[2], postulante, 80, postulantes_actuales, 3*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[13], postulante, 80, postulantes_actuales, 9*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[6], postulante, 25, postulantes_actuales, 4*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[15], postulante, 100, postulantes_actuales, 10*2)
                if(semaforo==False):
                    semaforo=almacenar_cambiante(carreras[16], postulante, 65, postulantes_actuales, 10*2)
            print("----------------------------------------------------------------------", i)
            i=0
        print("Almacenado completo")
        ###Manejo del excel a entregar
        insertar(carreras) ###Creacion y llenado del excel final
        todo=open("Admision UTEM.xlsx", 'rb').read()  ###Lectura del excel creado
        exc_64=base64.b64encode(todo).decode('UTF-8') ###Guardado en base64
        print("Archivo generado")
        ###Retorno del nombre del archivo, el tipo MIME, y el string base64 del excel
        yield("Admision UTEM.xlsx") ###Nombre del archivo excel
        for t in guess_type("Admision UTEM.xlsx"): ###Ciclo para entregar el tipo mime del excel
            if(t==None):
                pass
            else:    
                yield(t)
                break
        yield(exc_64) ###Devolucion del string base64 del excel

############################################################      Declaracion API para consumo      #############################################################
application = Application(
    [
        psuService ###Declaracion para poder consumir la API
    ],
    tns = 'spyne.examples.hello.soap',
    in_protocol = Soap11(), ###Especificacion de recibimiento de datos mediante protocolo SOAP11
    out_protocol = Soap11() ###Especificacion de entrega de datos mediante protocolo SOAP11
)

##########################################################      Main (Levantamiento del servidor)      ##########################################################
if __name__ == '__main__':
    # You can use any Wsgi server. Here, we chose
    # Python's built-in wsgi server but you're not
    # supposed to use it in production.
    from wsgiref.simple_server import make_server
    wsgi_app = WsgiApplication(application, chunked=True, max_content_length=2097152*100, block_length=1024*1024*500)
    server = make_server('127.0.0.1', 8000, wsgi_app) ###Activacion del servidor en ip 127.0.0.1 (Localhost), en el puerto 8000
    print("\nServidor en Linea") ###Aviso en terminal de que el servidor esta operativo
    server.serve_forever() ###Activacion del servidor
