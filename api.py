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

def ordenar(carrera): ###Funcion encargada de ordenar el listado de alumnos de una carrera; utiliza el metodo Quicksort; el parametro que recive es una lista
    tope=len(carrera)
    izquierda=[]
    derecha=[]
    centro=[]
    if(tope>1): ###Corrobora caso en el que solo ahi un elemento; en caso de tener mas de 1 elemento
        pivote=carrera[0][1] ###Define el pivote para separar en elementos mayores, menores o iguales a este
        for i in carrera:
            if(i[1]>pivote):    ###Si es mayor, va a una lista llamada "Izquierda"
                izquierda.append(i)
            elif(i[1]==pivote): ###Si es igual, va a una lista llamada "Centro"
                centro.append(i)
            elif(i[1]<pivote):  ###Si es menor, va a una lista llamada "Derecha"
                derecha.append(i)
        return ordenar(izquierda)+centro+ordenar(derecha) ###Finalmente, regresa la union de las 3 listas, pero aplicandole esta misma funcion a izquierda y derecha
    else:
        return carrera ###En el caso de solo ser 1 elemento, se devuelve directamente el arreglo, ya que no ahi nada que ordenar

def almacenar(carreras, datos, max_ing): ###Funcion que realiza el guardado de los estudiantes en las listas correspondientes; recibe como parametros, una lista, un par de datos [RUT, PUNTAJE] y el rango maximo de almacenaje
    sw=0 ###Variable importante, permite dentro del sistema, identificar si ya se realizo el almacenamiento del valor ingresado
    n=len(carreras)
    inicio=0
    if(n==max_ing): ###En funcion de la cantidad de elementos en la lista, es su funcionamiento, en el caso de que se encuentre a tope la lista
        if(datos[1]<carreras[max_ing-1][1]): ###Se realizara una comprobacion sobre si el nuevo puntaje es mayor que el mas pequeño; en caso de serlo, se devuelve inmediatemete, ya que no ingresara al listado por esa misma razon
            return carreras
        elif(datos[1]>=carreras[209][1]):
            inicio=0
        elif(datos[1]<carreras[209][1] and datos[1]>=carreras[419][1]):
            inicio=210
        elif(datos[1]<carreras[419][1] and datos[1]>=carreras[629][1]):
            inicio=210*2
        elif(datos[1]<carreras[629][1] and datos[1]>=carreras[839][1]):
            inicio=210*3
        elif(datos[1]<carreras[839][1] and datos[1]>=carreras[1049][1]):
            inicio=210*4
        elif(datos[1]<carreras[1049][1] and datos[1]>=carreras[1259][1]):
            inicio=210*5
        elif(datos[1]<carreras[1259][1] and datos[1]>=carreras[1469][1]):
            inicio=210*6
        elif(datos[1]<carreras[1469][1] and datos[1]>=carreras[1679][1]):
            inicio=210*7
        elif(datos[1]<carreras[1679][1] and datos[1]>=carreras[1889][1]):
            inicio=210*8
        elif(datos[1]<carreras[1889][1] and datos[1]>=carreras[2099][1]):
            inicio=210*9
        for posicion in range (inicio, max_ing): ###En caso de ser mas grande que el mas pequeño, se procedera a identificar mediante un for...
            if(carreras[posicion][1]<=datos[1]):
                carreras=carreras[0:(posicion)]+[datos]+carreras[(posicion):2099]
                return carreras
                    
        return carreras
    elif(n>=0 and n<(max_ing-1)): ###En caso de que aun no se llegue al tope, simplemente se iran agregando los valores a la lista
        carreras.append(datos)
        return carreras
    elif(n==(max_ing-1)): ###Y, en el caso de que tras ingresar este valor, se alcance el tope, tras ingresarlo, se realizara un ordenamiento descendente de la lista. 
        carreras.append(datos)
        return ordenar(carreras)

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
        matriculados=[]      ###Listado de alumnos ya matriculados
        i=0
        carreras=[] ###Lista de listas (listado de carreras)
        for i in range(0, 28):
            carreras.append([])

        todos = []  ###Lista de listas (listado de los mejores por area)
        for i in range(0, 12):
            todos.append([])
        
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
        print(len(message))
        if(len(message)<2101): ###Comprobador de que consta con la cantidad minima de lineas para el funcionamiento del sistema
            yield("El documento .csv enviado contiene una menor cantidad de personas de minimas requeridas (2101 personas)")
            return 0
        print("Datos corroborados")
        q=0
        ###Ciclo iterativo linea por linea para obtener toda la informacion del documento recibido
        for linea in message: 
            if(len(linea)!=0): ###Condicion para detectar si el arreglo esta vacio (ultima linea), o tienen contenido
                linea=linea.split(";") ###Se realiza la separacion de los valores

                if(q%10000==0):
                    print(q)

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
                todos[0]=almacenar(todos[0], [rut,c1], 2100)
                todos[1]=almacenar(todos[1], [rut,c2], 2100)
                todos[2]=almacenar(todos[2], [rut,c3], 2100)
                todos[3]=almacenar(todos[3], [rut,c4_7], 2100)
                todos[4]=almacenar(todos[4], [rut,c8], 2100)
                todos[5]=almacenar(todos[5], [rut,c9_10], 2100)
                todos[6]=almacenar(todos[6], [rut,c11], 2100)
                todos[7]=almacenar(todos[7], [rut,c12_13], 2100)
                todos[8]=almacenar(todos[8], [rut,c14_15], 2100)
                todos[9]=almacenar(todos[9], [rut,c16_17], 2100)
                todos[10]=almacenar(todos[10], [rut,c18], 2100)
                todos[11]=almacenar(todos[11], [rut,c19_28], 2100)
            else: ###Caso de la ultima linea (linea vacia)
                pass
            q=q+1
        print("Datos almacenados")
        ###Sector en el que se procede a generar los listados de matriculados por carrera
        for i in range(0,12):
            posicion=0               ###Variable para recorrer listado de los mejores de areas con 1 carrera
            posiciones_par=[0,0]     ###Variable para recorrer listado de los mejores de areas con  2 carrera
            posicion_tetra=[0,0,0,0] ###Variable para recorrer listado de los mejores de areas con 4 carrera
            posicion_ing=[0,0,0,0,0,0,0,0,0,0] ###Variable para recorrer listado de los mejores en el area area de ingenieria
            
            if(i==0): ###Area 1: 1 carrera
                while(len(carreras[0])<35): ###Se utiliza un ciclo para...
                    carreras[0]=almacenar(carreras[0],todos[i][posicion], 35) ###...Poblar la lista de la carrera correspondiente
                    matriculados.append(todos[i][posicion][0]) ###Luego registrar al alumno matriculado
                    posicion=posicion+1                        ###y pasar a la siguiente posicion del listado de mejores postulantes
                    
            elif(i==1): ###Area 2: 1 carrera
                while(len(carreras[1])<35):
                    if(todos[i][posicion][0] in matriculados): ###A partir del Area 2, se añade una verificacion, la cual es si el alumno ya esta o no matriculado
                        posicion=posicion+1  ###De estarlo, se pasa al siguiente en la lista de mejores postulantes
                    else: ###En el caso de no estarlo, se procede a registrarlo, tal cual como se hizo en el Area 1
                        carreras[1]=almacenar(carreras[1],todos[i][posicion], 35)
                        matriculados.append(todos[i][posicion][0])
                        posicion=posicion+1
                        
            elif(i==2): ###Area 3: 1 carrera
                while(len(carreras[2])<80):
                    if(todos[i][posicion][0] in matriculados):
                        posicion=posicion+1
                    else:
                        carreras[2]=almacenar(carreras[2],todos[i][posicion], 80)
                        matriculados.append(todos[i][posicion][0])
                        posicion=posicion+1
                        
            elif(i==3): ###Area 4: 4 carreras
                while((len(carreras[3])+len(carreras[4])+len(carreras[5])+len(carreras[6]))<270): ###En los casos con mas de una carrera por area, se hace lo siguiente:
                    if(n[0]==0): ###Mediante una verificacion con las variables de apoyo creadas antes, se va agregando estudiante una a uno en cada carrera; en cada caso...
                        if(len(carreras[3])==125): ###Se corrobora que si esta esta ya completa o no, en caso de estarlo, se pasa a la siguiente carrera
                            pass
                        else: ###En caso de no estar llena, se realiza el mismo procedimiento que en las areas anteriores
                            cant_actual=len(carreras[3])
                            while(cant_actual==len(carreras[3])):
                                
                                if(todos[i][posicion_tetra[0]][0] in matriculados):
                                    posicion_tetra[0]=posicion_tetra[0]+1
                                else:
                                    carreras[3]=almacenar(carreras[3],todos[i][posicion_tetra[0]], 125)
                                    matriculados.append(todos[i][posicion_tetra[0]][0])
                                    posicion_tetra[0]=posicion_tetra[0]+1
                        n[0]=1 ###Se modifica la variable para poder pasar a la siguiente carrera del Area en cuestion
                    elif(n[0]==1):
                        if(len(carreras[4])==30):
                            pass
                        else:
                            cant_actual=len(carreras[4])
                            while(cant_actual==len(carreras[4])):
                                if(todos[i][posicion_tetra[1]][0] in matriculados):
                                    posicion_tetra[1]=posicion_tetra[1]+1
                                else:
                                    carreras[4]=almacenar(carreras[4],todos[i][posicion_tetra[1]], 30)
                                    matriculados.append(todos[i][posicion_tetra[1]][0])
                                    posicion_tetra[1]=posicion_tetra[1]+1
                        n[0]=2
                    elif(n[0]==2):
                        if(len(carreras[5])==90):
                            pass
                        else:
                            cant_actual=len(carreras[5])
                            while(cant_actual==len(carreras[5])):
                                if(todos[i][posicion_tetra[2]][0] in matriculados):
                                    posicion_tetra[2]=posicion_tetra[2]+1
                                else:
                                    carreras[5]=almacenar(carreras[5],todos[i][posicion_tetra[2]], 90)
                                    matriculados.append(todos[i][posicion_tetra[2]][0])
                                    posicion_tetra[2]=posicion_tetra[2]+1
                        n[0]=3
                    elif(n[0]==3):
                        if(len(carreras[6])==25):
                            pass
                        else:
                            cant_actual=len(carreras[6])
                            while(cant_actual==len(carreras[6])):
                                if(todos[i][posicion_tetra[3]][0] in matriculados):
                                    posicion_tetra[3]=posicion_tetra[3]+1
                                else:
                                    carreras[6]=almacenar(carreras[6],todos[i][posicion_tetra[3]], 25)
                                    matriculados.append(todos[i][posicion_tetra[3]][0])
                                    posicion_tetra[3]=posicion_tetra[3]+1
                        n[0]=0 ###Cuando se llega a la ultima carrera del area, el valor se reinicia, para volver a la primera carrera del grupo
                        
            elif(i==4): ###Area 5: 1 carera
                while(len(carreras[7])<100):
                    if(todos[i][posicion][0] in matriculados):
                        posicion=posicion+1
                    else:
                        carreras[7]=almacenar(carreras[7],todos[i][posicion], 100)
                        matriculados.append(todos[i][posicion][0])
                        posicion=posicion+1
                        
            elif(i==5): ###Area 6: 2 carreras
                while((len(carreras[8])+len(carreras[9]))<200):
                    if(n[1]==0):
                        if(len(carreras[8])==100):
                            pass
                        else:
                            cant_actual=len(carreras[8])
                            while(cant_actual==len(carreras[8])):
                                if(todos[i][posiciones_par[0]][0] in matriculados):
                                    posiciones_par[0]=posiciones_par[0]+1
                                else:
                                    carreras[8]=almacenar(carreras[8],todos[i][posiciones_par[0]], 100)
                                    matriculados.append(todos[i][posiciones_par[0]][0])
                                    posiciones_par[0]=posiciones_par[0]+1
                        n[1]=1
                    elif(n[1]==1):
                        if(len(carreras[9])==100):
                            pass
                        else:
                            cant_actual=len(carreras[9])
                            while(cant_actual==len(carreras[9])):
                                if(todos[i][posiciones_par[1]][0] in matriculados):
                                    posiciones_par[1]=posiciones_par[1]+1
                                else:
                                    carreras[9]=almacenar(carreras[9],todos[i][posiciones_par[1]], 100)
                                    matriculados.append(todos[i][posiciones_par[1]][0])
                                    posiciones_par[1]=posiciones_par[1]+1
                        n[1]=0
                        
            elif(i==6): ###Area 7: 1 carrera1
                while(len(carreras[10])<30):
                    if(todos[i][posicion][0] in matriculados):
                        posicion=posicion+1
                    else:
                        carreras[10]=almacenar(carreras[10],todos[i][posicion], 30)
                        matriculados.append(todos[i][posicion][0])
                        posicion=posicion+1
                        
            elif(i==7): ###Area 8: 2 carreras
                while((len(carreras[11])+len(carreras[12]))<90):
                    if(n[2]==0):
                        if(len(carreras[11])==60):
                            pass
                        else:
                            cant_actual=len(carreras[11])
                            while(cant_actual==len(carreras[11])):
                                if(todos[i][posiciones_par[0]][0] in matriculados):
                                    posiciones_par[0]=posiciones_par[0]+1
                                else:
                                    carreras[11]=almacenar(carreras[11],todos[i][posiciones_par[0]], 60)
                                    matriculados.append(todos[i][posiciones_par[0]][0])
                                    posiciones_par[0]=posiciones_par[0]+1
                        n[2]=1
                    elif(n[2]==1):
                        if(len(carreras[12])==30):
                            pass
                        else:
                            cant_actual=len(carreras[12])
                            while(cant_actual==len(carreras[12])):
                                if(todos[i][posiciones_par[1]][0] in matriculados):
                                    posiciones_par[1]=posiciones_par[1]+1
                                else:
                                    carreras[12]=almacenar(carreras[12],todos[i][posiciones_par[1]], 30)
                                    matriculados.append(todos[i][posiciones_par[1]][0])
                                    posiciones_par[1]=posiciones_par[1]+1
                        n[2]=0
                        
            elif(i==8): ###Area 9: 2 carreras
                while((len(carreras[13])+len(carreras[14]))<120):
                    if(n[3]==0):
                        if(len(carreras[13])==80):
                            pass
                        else:
                            cant_actual=len(carreras[13])
                            while(cant_actual==len(carreras[13])):
                                if(todos[i][posiciones_par[0]][0] in matriculados):
                                    posiciones_par[0]=posiciones_par[0]+1
                                else:
                                    carreras[13]=almacenar(carreras[13],todos[i][posiciones_par[0]], 80)
                                    matriculados.append(todos[i][posiciones_par[0]][0])
                                    posiciones_par[0]=posiciones_par[0]+1
                        n[3]=1
                    elif(n[3]==1):
                        if(len(carreras[14])==40):
                            pass
                        else:
                            cant_actual=len(carreras[14])
                            while(cant_actual==len(carreras[14])):
                                if(todos[i][posiciones_par[1]][0] in matriculados):
                                    posiciones_par[1]=posiciones_par[1]+1
                                else:
                                    carreras[14]=almacenar(carreras[14],todos[i][posiciones_par[1]], 40)
                                    matriculados.append(todos[i][posiciones_par[1]][0])
                                    posiciones_par[1]=posiciones_par[1]+1
                        n[3]=0
                        
            elif(i==9): ###Area 10: 2 carreras
                while((len(carreras[15])+len(carreras[16]))<165):
                    if(n[4]==0):
                        if(len(carreras[15])==100):
                            pass
                        else:
                            cant_actual=len(carreras[15])
                            while(cant_actual==len(carreras[15])):
                                if(todos[i][posiciones_par[0]][0] in matriculados):
                                    posiciones_par[0]=posiciones_par[0]+1
                                else:
                                    carreras[15]=almacenar(carreras[15],todos[i][posiciones_par[0]], 100)
                                    matriculados.append(todos[i][posiciones_par[0]][0])
                                    posiciones_par[0]=posiciones_par[0]+1
                        n[4]=1
                    elif(n[4]==1):
                        if(len(carreras[16])==65):
                            pass
                        else:
                            cant_actual=len(carreras[16])
                            while(cant_actual==len(carreras[16])):
                                if(todos[i][posiciones_par[1]][0] in matriculados):
                                    posiciones_par[1]=posiciones_par[1]+1
                                else:
                                    carreras[16]=almacenar(carreras[16],todos[i][posiciones_par[1]], 65)
                                    matriculados.append(todos[i][posiciones_par[1]][0])
                                    posiciones_par[1]=posiciones_par[1]+1
                        n[4]=0
                        
            elif(i==10): ###Area 11: 1 carrera
                while(len(carreras[17])<95):
                    if(todos[i][posicion][0] in matriculados):
                        posicion=posicion+1
                    else:
                        carreras[17]=almacenar(carreras[17],todos[i][posicion], 95)
                        matriculados.append(todos[i][posicion][0])
                        posicion=posicion+1
                        
            elif(i==11): ###Area 12: 10 carreras
                while((len(carreras[18])+len(carreras[19])+len(carreras[20])+len(carreras[21])+len(carreras[22])+len(carreras[23])+len(carreras[24])+len(carreras[25])+len(carreras[26])+len(carreras[27]))<835):
                    if(n[5]==0):
                        if(len(carreras[18])==25):
                            pass
                        else:
                            cant_actual=len(carreras[18])
                            while(cant_actual==len(carreras[18])):
                                if(todos[i][posicion_ing[0]][0] in matriculados):
                                    posicion_ing[0]=posicion_ing[0]+1
                                else:
                                    carreras[18]=almacenar(carreras[18],todos[i][posicion_ing[0]], 25)
                                    matriculados.append(todos[i][posicion_ing[0]][0])
                                    posicion_ing[0]=posicion_ing[0]+1
                        n[5]=1
                    elif(n[5]==1):
                        if(len(carreras[19])==25):
                            pass
                        else:
                            cant_actual=len(carreras[19])
                            while(cant_actual==len(carreras[19])):
                                if(todos[i][posicion_ing[1]][0] in matriculados):
                                    posicion_ing[1]=posicion_ing[1]+1
                                else:
                                    carreras[19]=almacenar(carreras[19],todos[i][posicion_ing[1]], 25)
                                    matriculados.append(todos[i][posicion_ing[1]][0])
                                    posicion_ing[1]=posicion_ing[1]+1
                        n[5]=2
                    elif(n[5]==2):
                        if(len(carreras[20])==130):
                            pass
                        else:
                            cant_actual=len(carreras[20])
                            while(cant_actual==len(carreras[20])):
                                if(todos[i][posicion_ing[2]][0] in matriculados):
                                    posicion_ing[2]=posicion_ing[2]+1
                                else:
                                    carreras[20]=almacenar(carreras[20],todos[i][posicion_ing[2]], 130)
                                    matriculados.append(todos[i][posicion_ing[2]][0])
                                    posicion_ing[2]=posicion_ing[2]+1
                        n[5]=3
                    elif(n[5]==3):
                        if(len(carreras[21])==200):
                            pass
                        else:
                            cant_actual=len(carreras[21])
                            while(cant_actual==len(carreras[21])):
                                if(todos[i][posicion_ing[3]][0] in matriculados):
                                    posicion_ing[3]=posicion_ing[3]+1
                                else:
                                    carreras[21]=almacenar(carreras[21],todos[i][posicion_ing[3]], 200)
                                    matriculados.append(todos[i][posicion_ing[3]][0])
                                    posicion_ing[3]=posicion_ing[3]+1
                        n[5]=4
                    elif(n[5]==4):
                        if(len(carreras[22])==60):
                            pass
                        else:
                            cant_actual=len(carreras[22])
                            while(cant_actual==len(carreras[22])):
                                if(todos[i][posicion_ing[2]][0] in matriculados):
                                    posicion_ing[2]=posicion_ing[2]+1
                                else:
                                    carreras[22]=almacenar(carreras[22],todos[i][posicion_ing[2]], 60)
                                    matriculados.append(todos[i][posicion_ing[2]][0])
                                    posicion_ing[2]=posicion_ing[2]+1
                        n[5]=5
                    elif(n[5]==5):
                        if(len(carreras[23])==80):
                            pass
                        else:
                            cant_actual=len(carreras[23])
                            while(cant_actual==len(carreras[23])):
                                if(todos[i][posicion_ing[2]][0] in matriculados):
                                    posicion_ing[2]=posicion_ing[2]+1
                                else:
                                    carreras[23]=almacenar(carreras[23],todos[i][posicion_ing[2]], 80)
                                    matriculados.append(todos[i][posicion_ing[2]][0])
                                    posicion_ing[2]=posicion_ing[2]+1
                        n[5]=6
                    elif(n[5]==6):
                        if(len(carreras[24])==90):
                            pass
                        else:
                            cant_actual=len(carreras[24])
                            while(cant_actual==len(carreras[24])):
                                if(todos[i][posicion_ing[2]][0] in matriculados):
                                    posicion_ing[2]=posicion_ing[2]+1
                                else:
                                    carreras[24]=almacenar(carreras[24],todos[i][posicion_ing[2]], 90)
                                    matriculados.append(todos[i][posicion_ing[2]][0])
                                    posicion_ing[2]=posicion_ing[2]+1
                        n[5]=7
                    elif(n[5]==7):
                        if(len(carreras[25])==60):
                            pass
                        else:
                            cant_actual=len(carreras[25])
                            while(cant_actual==len(carreras[25])):
                                if(todos[i][posicion_ing[2]][0] in matriculados):
                                    posicion_ing[2]=posicion_ing[2]+1
                                else:
                                    carreras[25]=almacenar(carreras[25],todos[i][posicion_ing[2]], 60)
                                    matriculados.append(todos[i][posicion_ing[2]][0])
                                    posicion_ing[2]=posicion_ing[2]+1
                        n[5]=8
                    elif(n[5]==8):
                        if(len(carreras[26])==105):
                            pass
                        else:
                            cant_actual=len(carreras[26])
                            while(cant_actual==len(carreras[26])):
                                if(todos[i][posicion_ing[2]][0] in matriculados):
                                    posicion_ing[2]=posicion_ing[2]+1
                                else:
                                    carreras[26]=almacenar(carreras[26],todos[i][posicion_ing[2]], 105)
                                    matriculados.append(todos[i][posicion_ing[2]][0])
                                    posicion_ing[2]=posicion_ing[2]+1
                        n[5]=9
                    elif(n[5]==9):
                        if(len(carreras[27])==60):
                            pass
                        else:
                            cant_actual=len(carreras[27])
                            while(cant_actual==len(carreras[27])):
                                if(todos[i][posicion_ing[2]][0] in matriculados):
                                    posicion_ing[2]=posicion_ing[2]+1
                                else:
                                    carreras[27]=almacenar(carreras[27],todos[i][posicion_ing[2]], 60)
                                    matriculados.append(todos[i][posicion_ing[2]][0])
                                    posicion_ing[2]=posicion_ing[2]+1
                        n[5]=0
        print("Listados generados")
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
