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
from mimetypes import guess_type, guess_extension ###Libreria para manejar y detectar tipos mime
import re ###Libreria para manejar y detectar tipos mime

############################################################      Funciones Externas Utilizadas      ############################################################
def mayor(persona): ###Funcion para detectar cual es la carrera con el mayor puntaje ponderado de un postulante
    mayor=0
    pos_mayor=0
    for i in range(2,len(persona), 2): ###Ciclo para revisar cada puntaje ponderado
        if(persona[i]>mayor): ###Si es mayor que la variable "mayor"...
            mayor=persona[i]  ###Se registra el puntaje ponderado...
            pos_mayor=persona[i-1] ###y el indice de este
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

def almacenar(carreras, datos, max_ing, expulsados, lugar): ###Funcion que realiza el guardado de los estudiantes en las listas correspondientes; recibe como parametros, una lista, el listado de datos del postulante, el rango maximo de almacenaje, la lista de personas a re-ordenar y la posicion del dato ponderado correspondiente
    n=len(carreras)
    inicio=0
    if(n==max_ing): ###En funcion de la cantidad de elementos en la lista, es su funcionamiento, en el caso de que se encuentre a tope la lista
        if(datos[lugar]<carreras[max_ing-1][lugar]): ###Caso en el que el postulante tiene un puntaje inferior que el postulante con el puntaje mas bajo
            expulsados.append(datos)
            return carreras
        elif(datos[lugar]==carreras[max_ing-1][lugar]): ###Caso en el que el postulante y el postulante con el puntaje mas bajo sean iguales
            return carreras
        ###------------------------------------------  Area de deteccion de ubicacion relativa
        ###En esta zona, en funcion de la cantidad maxima de postulantes posibles a registrar, se
        ###detecta el area relativa que tendria dentro del listado; esto se hace mediante revisar
        ###los limites dentro de rangos predefinidos, en funcion  de un numeri divisor de la cant. total
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
            elif(datos[lugar]<=carreras[60][lugar] and datos[lugar]>=carreras[79][lugar]):
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
        ###-----------------------------------------------------------------------------------
        for posicion in range (inicio, max_ing): ###En caso de ser mas grande que el mas pequeño, se procedera a identificar mediante un for...
            if(carreras[posicion][lugar]<=datos[lugar]):
                expulsados.append(carreras[max_ing-1])
                carreras=carreras[0:(posicion)]+[datos]+carreras[(posicion):(max_ing-1)]
                return carreras

    elif(n>=0 and n<(max_ing-1)): ###En caso de que aun no se llegue al tope, simplemente se iran agregando los valores a la lista
        carreras.append(datos)
        return carreras
    elif(n==(max_ing-1)): ###Y, en el caso de que tras ingresar este valor, se alcance el tope, tras ingresarlo, se realizara un ordenamiento descendente de la lista. 
        carreras.append(datos)
        return ordenar(carreras, lugar)

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
        ###--------------------------- Area para identificar la posicion de los datos ponderados para la respectiva carrera;
        ###En funcion del indice obtenido, se sabe si se trabaja con las ponderaciones de su respectiva area
        if(indice==0):
            indice_datos=2
        elif(indice==1):
            indice_datos=4
        elif(indice==2):
            indice_datos=6
        elif(indice>=3 and indice<=6):
            indice_datos=8
        elif(indice==7):
            indice_datos=10
        elif(indice==9 or indice==8):
            indice_datos=12
        elif(indice==10):
            indice_datos=14
        elif(indice==12 or indice==11):
            indice_datos=16
        elif(indice==14 or indice==13):
            indice_datos=18
        elif(indice==16 or indice==15):
            indice_datos=20
        elif(indice==17):
            indice_datos=22
        elif(indice>=18):
            indice_datos=24
        ###-----------------------------------------------------------------------------------
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
            hoja['C'+str(fila)] = dato[indice_datos]
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
                if(((matematicas+lenguaje)/2)>=float(450)):
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
                    lugar=mayor(postulante) ###Se detecta cual es el puntaje mas alto, para luego internar ingresarlo en el area correspondiente; en caso de no entrar, se registra para su posterior re ubicacion
                    if(lugar==1):
                        carreras[0]=almacenar(carreras[0], postulante, 35, postulantes_anteriores, lugar*2)
                    elif(lugar==2):
                        carreras[1]=almacenar(carreras[1], postulante, 35, postulantes_anteriores, lugar*2)
                    elif(lugar==3):
                        carreras[2]=almacenar(carreras[2], postulante, 80, postulantes_anteriores, lugar*2)
                    elif(lugar==4):
                        if(len(carreras[3])<125):
                            carreras[3]=almacenar(carreras[3], postulante, 125, postulantes_anteriores, lugar*2)
                        elif(len(carreras[4])<30):
                            carreras[4]=almacenar(carreras[4], postulante, 30, postulantes_anteriores, lugar*2)
                        elif(len(carreras[5])<90):
                            carreras[5]=almacenar(carreras[5], postulante, 90, postulantes_anteriores, lugar*2)
                        else:
                            carreras[6]=almacenar(carreras[6], postulante, 25, postulantes_anteriores, lugar*2)
                    elif(lugar==5):
                        carreras[7]=almacenar(carreras[7], postulante, 100, postulantes_anteriores, lugar*2)
                    elif(lugar==6):
                        if(len(carreras[8])<100):
                            carreras[8]=almacenar(carreras[8], postulante, 100, postulantes_anteriores, lugar*2)
                        else:
                            carreras[9]=almacenar(carreras[9], postulante, 100, postulantes_anteriores, lugar*2)
                    elif(lugar==7):
                        carreras[10]=almacenar(carreras[10], postulante, 30, postulantes_anteriores, lugar*2)
                    elif(lugar==8):
                        if(len(carreras[11])<60):
                            carreras[11]=almacenar(carreras[11], postulante, 60, postulantes_anteriores, lugar*2)
                        else:
                            carreras[12]=almacenar(carreras[12], postulante, 30, postulantes_anteriores, lugar*2)
                    elif(lugar==9):
                        if(len(carreras[13])<80):
                            carreras[13]=almacenar(carreras[13], postulante, 80, postulantes_anteriores, lugar*2)
                        else:
                            carreras[14]=almacenar(carreras[14], postulante, 40, postulantes_anteriores, lugar*2)
                    elif(lugar==10):
                        if(len(carreras[15])<100):
                            carreras[15]=almacenar(carreras[15], postulante, 100, postulantes_anteriores, lugar*2)
                        else:
                            carreras[16]=almacenar(carreras[16], postulante, 65, postulantes_anteriores, lugar*2)
                    elif(lugar==11):
                        carreras[17]=almacenar(carreras[17], postulante, 95, postulantes_anteriores, lugar*2)
                    elif(lugar==12):
                        if(len(carreras[18])<25):
                            carreras[18]=almacenar(carreras[18], postulante, 25, postulantes_anteriores, lugar*2)
                        elif(len(carreras[19])<25):
                            carreras[19]=almacenar(carreras[19], postulante, 25, postulantes_anteriores, lugar*2)
                        elif(len(carreras[20])<130):
                            carreras[20]=almacenar(carreras[20], postulante, 130, postulantes_anteriores, lugar*2)
                        elif(len(carreras[21])<200):
                            carreras[21]=almacenar(carreras[21], postulante, 200, postulantes_anteriores, lugar*2)
                        elif(len(carreras[22])<60):
                            carreras[22]=almacenar(carreras[22], postulante, 60, postulantes_anteriores, lugar*2)
                        elif(len(carreras[23])<80):
                            carreras[23]=almacenar(carreras[23], postulante, 80, postulantes_anteriores, lugar*2)
                        elif(len(carreras[24])<90):
                            carreras[24]=almacenar(carreras[24], postulante, 90, postulantes_anteriores, lugar*2)
                        elif(len(carreras[25])<60):
                            carreras[25]=almacenar(carreras[25], postulante, 60, postulantes_anteriores, lugar*2)
                        elif(len(carreras[26])<105):
                            carreras[26]=almacenar(carreras[26], postulante, 105, postulantes_anteriores, lugar*2)
                        else:
                            carreras[27]=almacenar(carreras[27], postulante, 60, postulantes_anteriores, lugar*2)
            else: ###Caso de la ultima linea (linea vacia)
                pass
        ###Se procede a almacenar y preparar los datos para el escenario de re ubicacion  
        postulantes_actuales=postulantes_anteriores

        ###---------------------------------------------------------------------------------------------------------------------------------------
        #Ciclo iterativo para la re ubicacion de los postulantes; mientras exista almenos una persona que se deba re ubicar, se realizara un ciclo
        while(len(postulantes_anteriores)!=0):
            postulantes_anteriores=[] ###Se limpia el registro anterior
            postulantes_anteriores=postulantes_actuales ###Se registra los postulantes a re ubicar en esta iteracion
            postulantes_actuales=[] ###Se limpia el almacenamiento de los nuevos postulantes que puedan terminar siendo re ubicados
            for postulante in postulantes_anteriores: ###Para cada postulante a re ubicar, se realiza el siguiente proceso PARA CADA CARRERA
                for i in range(0, 29): ###Ciclo para revisar por cada carrera
                    if(i==0): ###Se detecta en cual carrera se encuentra
                        if(len(carreras[11])==60): ###Se comprueba si esta carrera ya esta llena y ordenada
                            if(postulante[16]<carreras[11][59][16]): ###Luego se comprueba si podria ingresar en la carrera; si no lo hace, no lo almacena, y pasa a la siguiente
                                pass
                            else: ###Si existe un posibilidad de entrar, pasa a almacenarlo y registrar a la persona que habra que re ubicar, y se termina las iteraciones con este postulante
                                carreras[11]=almacenar(carreras[11], postulante, 60, postulantes_actuales, 8*2)
                                break 
                        else: ###En caso de no estar llena ni ordenada, si ingresa, y cuando se llene la carrera, se ordenara esta misma
                            carreras[11]=almacenar(carreras[11], postulante, 60, postulantes_actuales, 8*2)
                            break
                    elif(i==1):
                        if(len(carreras[22])==60):
                            if(postulante[24]<carreras[22][59][24]):
                                pass
                            else:
                                carreras[22]=almacenar(carreras[22], postulante, 60, postulantes_actuales, 12*2)
                                break
                        else:
                            carreras[22]=almacenar(carreras[22], postulante, 60, postulantes_actuales, 12*2)
                            break
                    elif(i==2):
                        if(len(carreras[20])==130):
                            if(postulante[24]<carreras[20][129][24]):
                                pass
                            else:
                                carreras[20]=almacenar(carreras[20], postulante, 130, postulantes_actuales, 12*2)
                                break
                        else:
                            carreras[20]=almacenar(carreras[20], postulante, 130, postulantes_actuales, 12*2)
                            break
                    elif(i==3):
                        if(len(carreras[7])==100):
                            if(postulante[10]<carreras[7][99][10]):
                                pass
                            else:
                                carreras[7]=almacenar(carreras[7], postulante, 100, postulantes_actuales, 5*2)
                                break
                        else:
                            carreras[7]=almacenar(carreras[7], postulante, 100, postulantes_actuales, 5*2)
                            break
                    elif(i==4):
                        if(len(carreras[0])==35):
                            if(postulante[2]<carreras[0][34][2]):
                                pass
                            else:
                                carreras[0]=almacenar(carreras[0], postulante, 35, postulantes_actuales, 1*2)
                                break
                        else:
                            carreras[0]=almacenar(carreras[0], postulante, 35, postulantes_actuales, 1*2)
                            break
                    elif(i==5):
                        if(len(carreras[17])==95):
                            if(postulante[22]<carreras[17][94][22]):
                                pass
                            else:
                                carreras[17]=almacenar(carreras[17], postulante, 95, postulantes_actuales, 11*2)
                                break
                        else:
                            carreras[17]=almacenar(carreras[17], postulante, 95, postulantes_actuales, 11*2)
                            break
                    elif(i==6):
                        if(len(carreras[26])==105):
                            if(postulante[24]<carreras[26][104][24]):
                                pass
                            else:
                                carreras[26]=almacenar(carreras[26], postulante, 105, postulantes_actuales, 12*2)
                                break
                        else:
                            carreras[26]=almacenar(carreras[26], postulante, 105, postulantes_actuales, 12*2)
                            break
                    elif(i==7):
                        if(len(carreras[24])==90):
                            if(postulante[24]<carreras[24][89][24]):
                                pass
                            else:
                                carreras[24]=almacenar(carreras[24], postulante, 90, postulantes_actuales, 12*2)
                                break
                        else:
                            carreras[24]=almacenar(carreras[24], postulante, 90, postulantes_actuales, 12*2)
                            break
                    elif(i==8):
                        if(len(carreras[18])==25):
                            if(postulante[24]<carreras[18][24][24]):
                                pass
                            else:
                                carreras[18]=almacenar(carreras[18], postulante, 25, postulantes_actuales, 12*2)
                                break
                        else:
                            carreras[18]=almacenar(carreras[18], postulante, 25, postulantes_actuales, 12*2)
                            break
                    elif(i==9):
                        if(len(carreras[21])==200):
                            if(postulante[24]<carreras[21][199][24]):
                                pass
                            else:
                                carreras[21]=almacenar(carreras[21], postulante, 200, postulantes_actuales, 12*2)
                                break
                        else:
                            carreras[21]=almacenar(carreras[21], postulante, 200, postulantes_actuales, 12*2)
                            break
                    elif(i==10):
                        if(len(carreras[23])==80):
                            if(postulante[24]<carreras[23][79][24]):
                                pass
                            else:
                                carreras[23]=almacenar(carreras[23], postulante, 80, postulantes_actuales, 12*2)
                                break
                        else:
                            carreras[23]=almacenar(carreras[23], postulante, 80, postulantes_actuales, 12*2)
                            break
                    elif(i==11):
                        if(len(carreras[3])==125):
                            if(postulante[8]<carreras[3][124][8]):
                                pass
                            else:
                                carreras[3]=almacenar(carreras[3], postulante, 125, postulantes_actuales, 4*2)
                                break
                        else:
                            carreras[3]=almacenar(carreras[3], postulante, 125, postulantes_actuales, 4*2)
                            break
                    elif(i==12):
                        if(len(carreras[19])==25):
                            if(postulante[24]<carreras[19][24][24]):
                                pass
                            else:
                                carreras[19]=almacenar(carreras[19], postulante, 25, postulantes_actuales, 12*2)
                                break
                        else:
                            carreras[19]=almacenar(carreras[19], postulante, 25, postulantes_actuales, 12*2)
                            break
                    elif(i==13):
                        if(len(carreras[25])==60):
                            if(postulante[24]<carreras[25][59][24]):
                                pass
                            else:
                                carreras[25]=almacenar(carreras[25], postulante, 60, postulantes_actuales, 12*2)
                                break
                        else:
                            carreras[25]=almacenar(carreras[25], postulante, 60, postulantes_actuales, 12*2)
                            break
                    elif(i==14):
                        if(len(carreras[9])==100):
                            if(postulante[12]<carreras[9][99][12]):
                                pass
                            else:
                                carreras[9]=almacenar(carreras[9], postulante, 100, postulantes_actuales, 6*2)
                                break
                        else:
                            carreras[9]=almacenar(carreras[9], postulante, 100, postulantes_actuales, 6*2)
                            break
                    elif(i==15):
                        if(len(carreras[27])==60):
                            if(postulante[24]<carreras[27][59][24]):
                                pass
                            else:
                                carreras[27]=almacenar(carreras[27], postulante, 60, postulantes_actuales, 12*2)
                                break
                        else:
                            carreras[27]=almacenar(carreras[27], postulante, 60, postulantes_actuales, 12*2)
                            break
                    elif(i==16):
                        if(len(carreras[8])==100):
                            if(postulante[12]<carreras[8][99][12]):
                                pass
                            else:
                                carreras[8]=almacenar(carreras[8], postulante, 100, postulantes_actuales, 6*2)
                                break
                        else:
                            carreras[8]=almacenar(carreras[8], postulante, 100, postulantes_actuales, 6*2)
                            break
                    elif(i==17):
                        if(len(carreras[14])==40):
                            if(postulante[18]<carreras[14][39][18]):
                                pass
                            else:
                                carreras[14]=almacenar(carreras[14], postulante, 40, postulantes_actuales, 9*2)
                                break
                        else:
                            carreras[14]=almacenar(carreras[14], postulante, 40, postulantes_actuales, 9*2)
                            break
                    elif(i==18):
                        if(len(carreras[12])==30):
                            if(postulante[16]<carreras[12][29][16]):
                                pass
                            else:
                                carreras[12]=almacenar(carreras[12], postulante, 30, postulantes_actuales, 8*2)
                                break
                        else:
                            carreras[12]=almacenar(carreras[12], postulante, 30, postulantes_actuales, 8*2)
                            break
                    elif(i==19):
                        if(len(carreras[10])==30):
                            if(postulante[14]<carreras[10][29][14]):
                                pass
                            else:
                                carreras[10]=almacenar(carreras[10], postulante, 30, postulantes_actuales, 7*2)
                                break
                        else:
                            carreras[10]=almacenar(carreras[10], postulante, 30, postulantes_actuales, 7*2)
                            break
                    elif(i==20):
                        if(len(carreras[4])==30):
                            if(postulante[8]<carreras[4][29][8]):
                                pass
                            else:
                                carreras[4]=almacenar(carreras[4], postulante, 30, postulantes_actuales, 4*2)
                                break
                        else:
                            carreras[4]=almacenar(carreras[4], postulante, 30, postulantes_actuales, 4*2)
                            break
                    elif(i==21):
                        if(len(carreras[5])==90):
                            if(postulante[8]<carreras[5][89][8]):
                                pass
                            else:
                                carreras[5]=almacenar(carreras[5], postulante, 90, postulantes_actuales, 4*2)
                                break
                        else:
                            carreras[5]=almacenar(carreras[5], postulante, 90, postulantes_actuales, 4*2)
                            break
                    elif(i==22):
                        if(len(carreras[1])==35):
                            if(postulante[4]<carreras[1][34][4]):
                                pass
                            else:
                                carreras[1]=almacenar(carreras[1], postulante, 35, postulantes_actuales, 2*2)
                                break
                        else:
                            carreras[1]=almacenar(carreras[1], postulante, 35, postulantes_actuales, 2*2)
                            break
                    elif(i==23):
                        if(len(carreras[2])==80):
                            if(postulante[6]<carreras[2][79][6]):
                                pass
                            else:
                                carreras[2]=almacenar(carreras[2], postulante, 80, postulantes_actuales, 3*2)
                                break
                        else:
                            carreras[2]=almacenar(carreras[2], postulante, 80, postulantes_actuales, 3*2)
                            break
                    elif(i==24):
                        if(len(carreras[13])==80):
                            if(postulante[18]<carreras[13][79][18]):
                                pass
                            else:
                                carreras[13]=almacenar(carreras[13], postulante, 80, postulantes_actuales, 9*2)
                                break
                        else:
                            carreras[13]=almacenar(carreras[13], postulante, 80, postulantes_actuales, 9*2)
                            break
                    elif(i==25):
                        if(len(carreras[6])==25):
                            if(postulante[8]<carreras[6][24][8]):
                                pass
                            else:
                                carreras[6]=almacenar(carreras[6], postulante, 25, postulantes_actuales, 4*2)
                                break
                        else:
                            carreras[6]=almacenar(carreras[6], postulante, 25, postulantes_actuales, 4*2)
                            break
                    elif(i==26):
                        if(len(carreras[15])==100):
                            if(postulante[20]<carreras[15][99][20]):
                                pass
                            else:
                                carreras[15]=almacenar(carreras[15], postulante, 100, postulantes_actuales, 10*2)
                                break
                        else:
                            carreras[15]=almacenar(carreras[15], postulante, 100, postulantes_actuales, 10*2)
                            break
                    elif(i==27):
                        if(len(carreras[16])==65):
                            if(postulante[20]<carreras[16][64][20]):
                                pass
                            else:
                                print(len(carreras[16]))
                                carreras[16]=almacenar(carreras[16], postulante, 65, postulantes_actuales, 10*2)
                                break
                        else:
                            carreras[16]=almacenar(carreras[16], postulante, 65, postulantes_actuales, 10*2)
                            break
                    elif(i==28):
                        break
        ###Ordenamiento en caso de no completarse el llenado de personas
        for indice in range(0,28): ###Se revisa cada carrera
            if(indice==0): ###Se identifica que valor es el importante para ordenar
                indice_datos=2
            elif(indice==1):
                indice_datos=4
            elif(indice==2):
                indice_datos=6
            elif(indice>=3 and indice<=6):
                indice_datos=8
            elif(indice==7):
                indice_datos=10
            elif(indice==9 or indice==8):
                indice_datos=12
            elif(indice==10):
                indice_datos=14
            elif(indice==12 or indice==11):
                indice_datos=16
            elif(indice==14 or indice==13):
                indice_datos=18
            elif(indice==16 or indice==15):
                indice_datos=20
            elif(indice==17):
                indice_datos=22
            elif(indice>=18):
                indice_datos=24
                
            if(indice in [0,1]): ###Luego para cada carrera que tiene cierta cantidad tope...
                if(len(carreras[indice])<35): ###Se corrobora si llega o no
                    carreras[indice]=ordenar(carreras[indice], indice_datos) ###En caso de no llegar, se ordena, en caso de estar lleno, no se hace nada
            elif(indice in [2,13,23]):
                if(len(carreras[indice])<80):
                    carreras[indice]=ordenar(carreras[indice], indice_datos)
            elif(indice in [3]):
                if(len(carreras[indice])<125):
                    carreras[indice]=ordenar(carreras[indice], indice_datos)
            elif(indice in [26]):
                if(len(carreras[indice])<105):
                    carreras[indice]=ordenar(carreras[indice], indice_datos)
            elif(indice in [21]):
                if(len(carreras[indice])<200):
                    carreras[indice]=ordenar(carreras[indice], indice_datos)
            elif(indice in [20]):
                if(len(carreras[indice])<130):
                    carreras[indice]=ordenar(carreras[indice], indice_datos)
            elif(indice in [17]):
                if(len(carreras[indice])<95):
                    carreras[indice]=ordenar(carreras[indice], indice_datos)
            elif(indice in [16]):
                if(len(carreras[indice])<65):
                    carreras[indice]=ordenar(carreras[indice], indice_datos)
            elif(indice in [14]):
                if(len(carreras[indice])<40):
                    carreras[indice]=ordenar(carreras[indice], indice_datos)
            elif(indice in [11,22,25,27]):
                if(len(carreras[indice])<60):
                    carreras[indice]=ordenar(carreras[indice], indice_datos)
            elif(indice in [7,8,9,15]):
                if(len(carreras[indice])<100):
                    carreras[indice]=ordenar(carreras[indice], indice_datos)
            elif(indice in [6,18,19]):
                if(len(carreras[indice])<25):
                    carreras[indice]=ordenar(carreras[indice], indice_datos)
            elif(indice in [4,10,12]):
                if(len(carreras[indice])<30):
                    carreras[indice]=ordenar(carreras[indice], indice_datos)
            elif(indice in [5,24]):
                if(len(carreras[indice])<90):
                    carreras[indice]=ordenar(carreras[indice], indice_datos)
        ###---------------------------------------------------------
        ###Manejo del excel a entregar
        insertar(carreras) ###Creacion y llenado del excel final
        todo=open("Admision UTEM.xlsx", 'rb').read()  ###Lectura del excel creado
        exc_64=base64.b64encode(todo).decode('UTF-8') ###Guardado en base64
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
    wsgi_app = WsgiApplication(application, chunked=True, max_content_length=2097152*100*10, block_length=1024*1024*500*10)
    server = make_server('127.0.0.1', 8000, wsgi_app) ###Activacion del servidor en ip 127.0.0.1 (Localhost), en el puerto 8000
    print("\nServidor en Linea") ###Aviso en terminal de que el servidor esta operativo
    server.serve_forever() ###Activacion del servidor
