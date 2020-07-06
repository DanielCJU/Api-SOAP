# Api-SOAP

_API de protocolo SOAP para el ramo de Computacion Paralela y Distribuida de la UTEM (Trabajo 1)_

### Pre-requisitos 📋

_Para la instalacion y correcto funcionamiento, se requiere lo siguiente:_

* [Python](Version 3.8) - Lenguaje empleado

_Mediante instalacion por pip (o pip3, dependiendo el caso de ya poseer python en el equipo), las siguientes librerias:_
* [Spyne](pip install spyne==2.13.2a0)(https://pypi.org/project/spyne/2.13.2a0/) - Manejador de dependencias
* [Openpyxl](Version 3.0.3)(pip install openpyxl)(https://pypi.org/project/openpyxl/) - Usado para generar RSS
* [lxml](Version 4.5.1.0.3)(pip install lxml)(https://pypi.org/project/lxml/) - Para validacion
* [Base64] - Usado para encode y decode base64
* [re] - Para tipo mime 
* [mimetypes] - Para tipo mime


### Despliegue 📦

_Para poder desplegar y consumir este servicio, se deben seguir los siguientes pasos_

_1)se debe realizar la instalacion de python, en su version 3.8; para esto, se puede descargar desde la pagina oficial de python(https://www.python.org/downloads/). Una vez instalado, se puede corroborar la version mediante la consola de comandos mediante el siguiente comando _

```
python --version
```

_En el caso de ya contar con python ya en el equipo (ejemplo de esto, es que el comando anterior arroje una version distinta de python), probar con el siguiente_

```
python3 --version
```

_2)Ya con python instalado, se procede a instalar las librerias correspondiente mediante el pip (pip3 en caso de tener que usar python3 para la version solicitada)_

```
pip install spyne==2.13.2a0
pip install openpyxl
pip install lxml
---- los siguientes pueden ya venir incluidos en python 3.8
pip install base64
pip install re
pip install mimetypes
```

_3)Ya con todas las dependencias instaladas, en la locacion del archivo api.py, mediante consola de comandos, activar el programa python (python3 en caso expresado anteriormente en el punto 1)_

```
python api.py
```

_Cuando el codigo muestre en la consola la frase "Servidor en Linea", significara que el servidor esta activado, en la ip 127.0.0.1 (local host, en el puerto 8000)_

_En el caso de consumir la api mediante SoapUI, la URL a utilizar seria la siguiente_

```
http://localhost:8000/?wsdl
```

## Ejecutando las pruebas ⚙️

_El software fue testeado con documentos de 100, 1000, 5000, 10000, 12000, 500000, 1000000 y 2000000 de participantes, siendo que en todos se presento un correcto funcionamiento estandar, y en el caso de 100 y 1000, retorno un excel el cual agrego a todos, pero no pudiendo completar todas las carreras debido a la falta de gente 
que postulo (el total de postulantes a matricular es de 2055 estudiantes)

## Notas adicionales 📖
* El string a recibir debe estar en base 64.
* Los elementos del archivo deben respetar la estructura expuesta en el PDF del problema (el cual se encuentra en la carpeta "Material de Apoyo")
* Enlace archivo puntajes.csv: https://drive.google.com/file/d/1v5yV9-jAjymUSEg27YgiJ3kOykknEU7v/view?usp=sharing

## Autores ✒️

* **Ricardo Aliste G.** - *Desarrollado/Documentación*
* **Daniel Cajas U.** - *Desarrollado*
* **Rodrigo Carmona R.** - *Documentación*




Plantilla utilizada para el readme creada por [Villanuevand](https://github.com/Villanuevand) 😊
