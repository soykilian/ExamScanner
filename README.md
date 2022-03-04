# Lectura de plantillas tipo test de la ETSIT-UPM con Raspberry Pi, Flask, OpenCV, omr-rbaron, mjpg-streamer, Pandas y smtplib  

![flujograma-python](https://imgur.com/WOFhEkm.png)
![flujograma-C](https://i.imgur.com/N6OUqIA.jpeg)
![hardware](https://i.imgur.com/XInRw4x.jpg)


Configuración en el cliente
======

Para facilitar el proceso de instalación, configuración, y uso de la herramienta, la dirección IP que se emplea para acceder a la Raspberry/servidor debe ser consistente (i.e. estática). En caso contrario, es recomendable emplear el host `DIRECCION_RPI` como dirección de la Raspberry/`DIRECCION_SERVIDOR` como dirección del servidor para que, en caso de producirse un cambio inesperado de la IP, resulte sencillo emplear la herramienta de nuevo. Para ello, modificaremos el fichero `hosts` del sistema operativo del cliente añadiendo al final del mismo la línea (suponiendo dirección IP = `192.168.1.123`):


### Opción a) Configuración para Raspberry Pi

- `192.168.1.123 DIRECCION_RPI` en el fichero `/etc/hosts`, como usuario root, en sistemas GNU/Linux
- `192.168.1.123 DIRECCION_RPI` en el fichero `/private/etc/hosts`, como usuario root, en sistemas OS X
- `192.168.1.123 DIRECCION_RPI` en el fichero `C:\Windows\System32\drivers\etc\hosts`, como administrador, en sistemas Windows

En caso de cambio de la IP de la Raspberry en el futuro simplemente debemos modificar esta última línea de manera conveniente.

### Opción b) Configuración para servidor en plataforma distinta a Raspberry (tomar fotos con el móvil)

- `192.168.1.123 DIRECCION_SERVIDOR` en el fichero `/etc/hosts`, como usuario root, en sistemas GNU/Linux
- `192.168.1.123 DIRECCION_SERVIDOR` en el fichero `/private/etc/hosts`, como usuario root, en sistemas OS X
- `192.168.1.123 DIRECCION_SERVIDOR` en el fichero `C:\Windows\System32\drivers\etc\hosts`, como administrador, en sistemas Windows

En caso de cambio de la IP del servidor en el futuro simplemente debemos modificar esta última línea de manera conveniente.


Opción a) Configuración e inicialización en Raspberry Pi
======

Se asume que partimos de una instalación _fresh_ de Raspbian OS con SSH habilitado y que conocemos la IP asignada a la interfaz de red (ethernet o Wi-Fi). Además, se considera que esta IP se ha configurado como estática previamente en la configuración del router que le proporciona acceso a la red, o bien en el fichero `/etc/dhcpcd.conf`, o bien hemos seguido el paso _Configuración en el cliente_.

Desde este momento, la dirección IP de la Raspberry será referida como `DIRECCION_RPI`.


### Instalación de la pantalla Adafruit TFT 2.8" resistiva

```shell
pi@raspberry:~$ cd ~
pi@raspberry:~$ sudo apt-get install python3-pip
pi@raspberry:~$ sudo pip3 install --upgrade adafruit-python-shell click==7.0
pi@raspberry:~$ git clone https://github.com/adafruit/Raspberry-Pi-Installer-Scripts.git
pi@raspberry:~$ cd Raspberry-Pi-Installer-Scripts
pi@raspberry:~$ sudo python3 adafruit-pitft.py --display=28r --rotation=90 --install-type=fbcp
```


### Instalación de mjpg-streamer

```shell
pi@raspberry:~$ cd ~
pi@raspberry:~$ sudo apt-get update
pi@raspberry:~$ sudo raspi-config
- Botón 6, Enable Camera. Yes, OK, Finish.
pi@raspberry:~$ sudo apt-get install git
pi@raspberry:~$ git clone https://github.com/jacksonliam/mjpg-streamer.git
pi@raspberry:~$ cd mjpg-streamer/mjpg-streamer-experimental/
pi@raspberry:~$ sudo apt-get install cmake
pi@raspberry:~$ sudo apt-get install python-imaging
pi@raspberry:~$ sudo apt-get install libjpeg-dev
pi@raspberry:~$ make CMAKE_BUILD_TYPE=Debug
pi@raspberry:~$ sudo make install
pi@raspberry:~$ echo 'export PATH=~/mjpg-streamer/mjpg-streamer-experimental:$PATH' >> ~/.bashrc
```


### Instalación de OpenCV

```shell
pi@raspberry:~$ cd ~
pi@raspberry:~$ sudo apt install libatlas3-base
pi@raspberry:~$ sudo python3 -m pip install opencv-python-headless
```


### Instalación de Flask

```shell
pi@raspberry:~$ cd ~
pi@raspberry:~$ sudo python3 -m pip install Flask Flask-Cors Flask-AutoIndex
```


### Instalación de Pandas

```shell
pi@raspberry:~$ cd ~
pi@raspberry:~$ sudo python3 -m pip install --upgrade numpy
pi@raspberry:~$ sudo python3 -m pip install pandas
```

### Instalación de requests

```shell
pi@raspberry:~$ cd ~
pi@raspberry:~$ sudo python3 -m pip install requests
```

### Clonación del repositorio `lector-plantillas-ETSIT`

```shell
pi@raspberry:~$ cd ~
pi@raspberry:~$ git clone https://USUARIO_GITHUB_AUTORIZADO@github.com/mguarinos/lector-plantillas-ETSIT
```

### Ejecución la herramienta (análisis de imágenes)

Se debe ejecutar el siguiente comando para iniciar el servidor Flask que se encargará de ejecutar el _pipeline_ del análisis de las imágenes.

```shell
python3 ~/lector-plantillas-ETSIT/server.py \
EMAIL_SMTP \
CONTRASEÑA_SMTP \
DOMINIO_SMTP \
PUERTO_SMTP
```

Ejemplo del comando:

```shell
python3 ~/lector-plantillas-ETSIT/server.py \
"pruebasSDG2@gmail.com" \
"manolete" \
"smtp.gmail.com" \
465
```

Además, debemos iniciar el servidor mjpg-streamer con el comando `mjpg_streamer -i "input_raspicam.so -x 2592 -y 1944 -rot 270"`, habilitando todas las funciones de previsualización y captura de imágenes.

> Estos comandos pueden automatizarse para ejecutarse al reiniciar el sistema operativo mediante tareas cron, tal y como se muestra en https://www.cyberciti.biz/faq/linux-execute-cron-job-after-system-reboot/


### Ejecución del programa en C para el control del teclado matricial y display

Modifique los pines GPIO necesarios en el fichero ~/lector-plantillas-ETSIT/teclado_con_display.c, tanto para el teclado como para el display. Tenga en cuenta que el display emplea un pin CLK.

```shell
cd ~/lector-plantillas-ETSIT/teclado_con_display
gcc -o main main.c -lwiringPi
./main
```


Opción b1) Configuración e inicialización de servidor en plataforma distinta a Raspberry (tomar fotos con el móvil), procedimiento manual
======

A modo de ejemplo se muestran los comandos que deben ejecutarse en un sistema operativo Debian (o derivados) con `Python3` y `git` instalado.

Se asume que partimos de una instalación de Xubuntu 20.04 y que conocemos la IP asignada a la interfaz de red del servidor (ethernet o Wi-Fi). Además, se considera que esta IP se ha configurado como estática previamente en la configuración del router que le proporciona acceso a la red, o bien en el fichero `/etc/dhcpcd.conf` del servidor, o bien hemos seguido el paso _Configuración en el cliente_.

Desde este momento, la dirección IP del servidor será referida como `DIRECCION_SERVIDOR`.

### Instalación de OpenCV

```shell
manuel@servidor:~$ cd ~
manuel@servidor:~$ sudo python3 -m pip install opencv-python
```


### Instalación de Flask

```shell
manuel@servidor:~$ cd ~
manuel@servidor:~$ sudo python3 -m pip install Flask Flask-Cors Flask-AutoIndex
```


### Instalación de Pandas

```shell
manuel@servidor:~$ cd ~
manuel@servidor:~$ sudo python3 -m pip install --upgrade numpy
manuel@servidor:~$ sudo python3 -m pip install pandas
```

### Instalación de requests

```shell
manuel@servidor:~$ cd ~
manuel@servidor:~$ sudo python3 -m pip install requests
```

### Clonación del repositorio `lector-plantillas-ETSIT`

```shell
manuel@servidor:~$ cd ~
manuel@servidor:~$ git clone https://USUARIO_GITHUB_AUTORIZADO@github.com/mguarinos/lector-plantillas-ETSIT
```

### Ejecución de la herramienta

Se debe ejecutar el siguiente comando para iniciar el servidor Flask que se encargará de ejecutar el _pipeline_ del análisis de las imágenes.

```shell
python3 ~/lector-plantillas-ETSIT/server.py \
EMAIL_SMTP \
CONTRASEÑA_SMTP \
DOMINIO_SMTP \
PUERTO_SMTP
```

Ejemplo del comando:

```shell
python3 ~/lector-plantillas-ETSIT/server.py \
"pruebasSDG2@gmail.com" \
"manolete" \
"smtp.gmail.com" \
465
```

> Este comando puede automatizarse para ejecutarse al reiniciar el sistema operativo mediante tareas cron, tal y como se muestra en https://www.cyberciti.biz/faq/linux-execute-cron-job-after-system-reboot/



Opción b2) Imagen Docker
======

A modo de ejemplo, se muestra el comando que debe ejecutarse en un sistema operativo con `Docker` instalado.

```shell
docker container run -d \
 -it \
 -p 5000:5000 \
 --name lector-plantillas \
 mguarinos/lector-plantillas \
 python3 server.py \
 EMAIL_SMTP \
 CONTRASEÑA_SMTP \
 DOMINIO_SMTP \
 PUERTO_SMTP
```

Ejemplo del comando:

```shell
docker container run -d \
 -it \
 -p 5000:5000 \
 --name lector-plantillas \
 mguarinos/lector-plantillas \
 python3 server.py \
 "pruebasSDG2@gmail.com" \
 "manolete" \
 "smtp.gmail.com" \
 465
```

> Este comando puede automatizarse para ejecutarse al reiniciar el sistema operativo mediante tareas cron, tal y como se muestra en https://www.cyberciti.biz/faq/linux-execute-cron-job-after-system-reboot/


Personalización del remitente, datos y alumnos del examen
======

### Remitente del email

Modificando los campos `EMAIL_SMTP`, `CONTRASEÑA_SMTP`, `DOMINIO_SMTP` y `PUERTO_SMTP` de los comandos anteriores obtendremos los resultados desesados.


### Datos del examen

En las líneas 20-28 del fichero `server.py` encontramos las siguientes constantes:

- `EXAMEN` define el asunto del mensaje que recibirá el alumno al recibir la imagen, respuestas y calificación en su dirección de correo electrónico.
- `EMAIL_COORDINADOR` es la dirección de correo electrónico a la que llegarán las fotos reconocidas incorrectamente y los exámenes con DNI inexistente en el fichero configurado en el apartado siguiente.
- `N_ALTERNATIVAS` es el número de respuestas posibles que tiene cada pregunta:
    - `{A, B} = 2`
    - `{A, B, C} = 3`
    - `{A, B, C, D} = 4`
    - `{A, B, C, D, E} = 5`

- `RESPUESTAS_CORRECTAS` es el array de respuestas correctas para cada uno de los modelos {1, 2, 3, 4} del examen.

Las respuestas incorrectas suman `-1/N_ALTERNATIVAS` a la calificación final del examen.

```python
EXAMEN = "INTRODUCCIÓN A LA INGENIERÍA DE TELECOMUNICACIÓN - EXAMEN FINAL"
EMAIL_COORDINADOR = "pruebasSDG2+coordinador@gmail.com"
N_ALTERNATIVAS = 5
RESPUESTAS_CORRECTAS = [
    ["A", "B", "C", "A", "B", "A", "C", "E", "E", "E", "C", "D"],
    ["C", "A", "B", "C", "A", "B", "A", "C", "E", "A", "B", "D"],
    ["A", "B", "C", "A", "B", "A", "C", "E", "A", "B", "C", "D"],
    ["A", "B", "A", "B", "C", "A", "C", "E", "A", "B", "C", "D"]
]
```

> No es posible modificar los datos de este apartado en la imagen Docker de manera sencilla. Queda a manos del lector los conocimientos necesarios para ello, así como el _Dockerfile_ por si lo considerara necesario.


### Alumnos con derecho a examen

Los datos de los alumnos deben configurarse previamente al examen, y conforman la "base de datos" con sus nombres, apellidos, DNIs y direcciones de correo electrónico, todo ello en el fichero `data.csv`, con el formato ```DNI,Surname,Name,Email,Version,Answers,Nota```. Se puede editar con el editor deseado (nano, mousepad, geany, libreoffice, openoffice, excel...)

A modo de ejemplo, se muestra el contenido del fichero para 4 alumnos:

#### Antes de realizar cualquier análisis de un examen:

|DNI     |Surname             |Name          |Email                        |Version|Answers|Nota|
|--------|--------------------|--------------|-----------------------------|-------|-------|----|
|12321   |Apellido1 Apellido2 |Nombre        |pruebasSDG2+prueba2@gmail.com|       |       |    |
|123456  |Apellido3 Apellido4 |Nombre        |pruebasSDG2+prueba3@gmail.com|       |       |    |
|1234789 |Apellido4 Apellido5 |Nombre        |pruebasSDG2+prueba3@gmail.com|       |       |    |
|541875  |Clerico da Costa    |Maria Victoria|mv.clerico@alumnos.upm.es    |       |       |    |
|49217746|Guarinos López      |Manuel        |m.guarinos@alumnos.upm.es    |       |       |    |
|99009310| PRUEBA             | PRUEBA       | prueba@prueba.com           |       |       |    |


```csv
DNI,Surname,Name,Email,Version,Answers,Nota
12321,Apellido1 Apellido2 ,Nombre,pruebasSDG2+prueba2@gmail.com,,,
123456,Apellido3 Apellido4 ,Nombre,pruebasSDG2+prueba3@gmail.com,,,
1234789,Apellido4 Apellido5,Nombre,pruebasSDG2+prueba3@gmail.com,,,
541875,Clerico da Costa,Maria Victoria,mv.clerico@alumnos.upm.es,,,
49217746,Guarinos López,Manuel,m.guarinos@alumnos.upm.es,,,
99009310, PRUEBA, PRUEBA, prueba@prueba.com,,,
```
#### Después de realizar un análisis sobre el alumno _Guarinos López, Manuel_:

|DNI     |Surname             |Name          |Email                        |Version|Answers|Nota|
|--------|--------------------|--------------|-----------------------------|-------|-------|----|
|12321   |Apellido1 Apellido2 |Nombre        |pruebasSDG2+prueba2@gmail.com|       |       |    |
|123456  |Apellido3 Apellido4 |Nombre        |pruebasSDG2+prueba3@gmail.com|       |       |    |
|1234789 |Apellido4 Apellido5 |Nombre        |pruebasSDG2+prueba3@gmail.com|       |       |    |
|541875  |Clerico da Costa    |Maria Victoria|mv.clerico@alumnos.upm.es    |       |       |    |
|49217746|Guarinos López      |Manuel        |m.guarinos@alumnos.upm.es    |       |       |9.0 |
|99009310| PRUEBA             |PRUEBA        | prueba@prueba.com           |       |       |    |


```csv
DNI,Surname,Name,Email,Version,Answers,Nota
12321,Apellido1 Apellido2 ,Nombre,pruebasSDG2+prueba2@gmail.com,,,
123456,Apellido3 Apellido4 ,Nombre,pruebasSDG2+prueba3@gmail.com,,,
1234789,Apellido4 Apellido5,Nombre,pruebasSDG2+prueba3@gmail.com,,,
541875,Clerico da Costa,Maria Victoria,mv.clerico@alumnos.upm.es,,,
49217746,Guarinos López,Manuel,m.guarinos@alumnos.upm.es,,,9.0
99009310, PRUEBA, PRUEBA, prueba@prueba.com,,,

```

> Con la imagen Docker no es posible modificar estos datos de manera sencilla. Una posible alternativa sería emplear el comando `docker exec -it lector-plantillas cat data.csv` para la lectura. Previsiblemente se habilitará un campo para la subida de este fichero en la interfaz web en futuras versiones. Otras alternativas quedan en manos de un lector familizarizado con contenerización.

Uso de la herramienta
======

> La carpeta `IMAGENES_EJEMPLO` incluye fotografías de ejemplo para probar la herramienta mediante el procedimiento `Escanear una imagen externa mediante petición HTTP POST` descrito en esta sección

Si se han seguido los pasos correctamente, tras reiniciar el sistema operativo todo debe funcionar adecuadamente.

### Tomar una foto de la cámara conectada a la Raspberry Pi mediante navegador web

Abrir la dirección `http://DIRECCION_RPI:5000/interfaz.html` en un navegador web y pulsar el botón _Tomar foto_ cuando se considere un resultado adecuado. La interfaz mostrará el resultado del análisis, mandará el email correspondiente, y modificará el fichero `data.csv`

### Tomar una foto de la cámara conectada a la Raspberry Pi mediante petición HTTP GET (análisis masivo)

Carecemos de previsualización de la cámara, salvo que accedamos a `http://DIRECCION_RPI:8080?action=stream`. En un sistema UNIX con la herramienta cURL se debe ejecutar la orden `curl http://DIRECCION_RPI:5000/get_answers` en una terminal. Devolverá un objeto JSON con el resultado del análisis, mandará el email correspondiente, y modificará el fichero `data.csv`
`

### Escanear una imagen externa mediante navegador web (subida desde ordenador, móvil...)

Permite subir ficheros externos, como fotografías tomadas con un móvil. Acceda a `http://DIRECCION_RPI:5000/interfaz.html` o `http://DIRECCION_SERVIDOR:5000/interfaz.html`. Presione el botón "subir foto", y seleccione la imagen deseada. Procesará la plantilla, mandará el email correspondiente, y modificará el fichero `data.csv`.


### Escanear una imagen externa mediante petición HTTP POST (análisis masivo)

> La carpeta `IMAGENES_EJEMPLO` incluye fotografías de ejemplo para probar la herramienta mediante el procedimiento `Escanear una imagen externa mediante petición HTTP POST` descrito en esta sección

Permite subir ficheros externos, como fotografías tomadas con un móvil, lotes de ficheros de manera automatizada.. En un sistema UNIX con la herramienta cURL se debe ejecutar la orden `curl --location --request POST 'http://DIRECCION_SERVIDOR:5000/get_answers' --form 'image=@RUTA_AL_FICHERO'` en una terminal. Devolverá un objeto JSON con el resultado del análisis, mandará el email correspondiente, y modificará el fichero `data.csv`.

Ejemplo de la llamada:

```curl --location --request POST 'http://DIRECCION_SERVIDOR:5000/get_answers' --form 'image=@"/home/manuel/Escritorio/lector-plantillas-ETSIT/imagen.jpg"'```
