# encoding= utf-8
"""
@author:Jabi Martin
@desc: Obtiene %Temperatura y humedad
"""
import paho.mqtt.publish as publish
import time
import httplib
import urllib
import json
import socket

import RPi.GPIO as GPIO   # Importamos las librerias necesarias para usar los pines GPIO


def bin2dec(string_num):  # Creamos una funcion para transformar de binario a decimal
    return str(int(string_num, 2))

USER_API_KEY = "9TNQC2RGM3Q0L07A"
# Establecer conexion TCP
server = "api.thingspeak.com"
connTCP = httplib.HTTPSConnection(server)
print("Estableciendo conexión con " + server)
connTCP.connect()
print("Conexion establecida")
print("Borrando info de Canales viejos")

method = "GET"
CHANNEL_ID0 = '680596'
WRITE_API_KEY0 = '8D2K6RKH4IRTKP72'
READ_API_KEY0 = "A4QVGC0XAREB70WI"
relative_uri = "/channels/" + str(CHANNEL_ID0) + "/feeds.json"
# definimos un diccionario, pares nombre-valor
headers = {'Host': server,
           'Content-Type': 'application/x-www-form-urlencoded'
          }
payload = {'api_key': READ_API_KEY0}
payload_encode = urllib.urlencode(payload)
headers['Content-Length'] = len(payload_encode)
print("Enviando ...")
connTCP.request(method, relative_uri, body=payload_encode, headers=headers)
print("Enviada Peticion de Lectura de canales gestionados")
respuesta = connTCP.getresponse()
status = respuesta.status
print(str(status))
if status == 200:
    contenido = respuesta.read()
    # print(contenido)
    contenido_json = json.loads(contenido)
    for i in range(0, len(contenido_json['feeds'])):
        CHANNEL_ID = contenido_json['feeds'][i]['field1']
        # READ_API_KEY = contenido_json['feeds'][i]['field2']
        print("Borrando fisicamente el Canal " + str(CHANNEL_ID) )
        method = "DELETE"
        relative_uri = "/channels/" + str(CHANNEL_ID) + ".json"
        # definimos un diccionario, pares nombre-valor
        headers = {'Host': server,
                   'Content-Type': 'application/x-www-form-urlencoded'
                   }
        payload = {'api_key': USER_API_KEY}
        payload_encode = urllib.urlencode(payload)
        headers['Content-Length'] = len(payload_encode)
        print("Enviando ...")
        connTCP.request(method, relative_uri, body=payload_encode, headers=headers)
        print("Enviada Borrado Channel " + str(CHANNEL_ID))
        respuesta = connTCP.getresponse()
        status = respuesta.status
        print(str(status))
        if status == 200:
            print("Borrado Channel" + str(CHANNEL_ID))
        else:
            print("Error Borrando Channel" + str(CHANNEL_ID))


    method = "DELETE"
    relative_uri = "/channels/" + str(CHANNEL_ID0) + "/feeds.json"
    # definimos un diccionario, pares nombre-valor
    headers = {'Host': server,
               'Content-Type': 'application/x-www-form-urlencoded'
               }
    payload = {'api_key': USER_API_KEY}
    payload_encode = urllib.urlencode(payload)
    headers['Content-Length'] = len(payload_encode)
    time.sleep(5)
    print("Enviando ...")
    connTCP.request(method, relative_uri, body=payload_encode, headers=headers)
    print("Enviada Peticion de limpieza de canal Gestor "+ str(CHANNEL_ID0))
    try:
        respuesta = connTCP.getresponse()
        status = respuesta.status
        print(str(status))
        if status == 200:
            print("Limpieza de Canal Gestor correcta")
    except Exception:
        print("Error en Limpieza de Canal Gestor")
else:
    exit()

# crear canal
method = "POST"
relative_uri = "/channels.json"
# definimos un diccionario, pares nombre-valor
headers = {'Host': server,
           'Content-Type': 'application/x-www-form-urlencoded'
           }
payload = {'api_key': USER_API_KEY,
           'name': 'Automatic channel',
           'description': 'New channel',
           'field1': 'Temperatura',
           'field2': 'Humedad'}
payload_encode = urllib.urlencode(payload)
headers['Content-Length'] = len(payload_encode)
time.sleep(15)
print("Enviando Crear Canal 1...")
connTCP.close()
connTCP = httplib.HTTPSConnection(server)
print("Estableciendo conexion con " + server)
connTCP.connect()
connTCP.request(method, relative_uri, body=payload_encode, headers=headers)
print("Enviada Peticion de creaccion de canal nuevo")
status = 0
while not (status >= 200):
    try:
        respuesta = connTCP.getresponse()
        status = respuesta.status
    except httplib.ResponseNotReady:
        print("Error Respuesta No disponible")
        time.sleep(1)
print(str(status))
contenido = respuesta.read()
# print(contenido)
contenido_json = json.loads(contenido)
CHANNEL_ID1 = contenido_json['id']
WRITE_API_KEY1 = contenido_json['api_keys'][0]['api_key']
READ_API_KEY1 = contenido_json['api_keys'][1]['api_key']
time.sleep(15)
print("Enviando Crear Canal 2")
connTCP.request(method, relative_uri, body=payload_encode, headers=headers)
print("Enviada Peticion de creaccion de canal nuevo")
respuesta = connTCP.getresponse()
status = respuesta.status
print(str(status))
contenido = respuesta.read()
# print(contenido)
contenido_json = json.loads(contenido)
CHANNEL_ID2 = contenido_json['id']
WRITE_API_KEY2 = contenido_json['api_keys'][0]['api_key']
READ_API_KEY2 = contenido_json['api_keys'][1]['api_key']


# Replace <channelID> with the channel ID
# Replace <apikey> with the WRITE_API_KEY
# Vamos a guardar en un canal Gestor la info de los canales creados
# de forma que podamos leer sus valores desde la pagina para acceder a los
# canales que realmente contienen los datos
topic1 = 'channels/' + str(CHANNEL_ID1) + '/publish/' + WRITE_API_KEY1
topic2 = 'channels/' + str(CHANNEL_ID2) + '/publish/' + WRITE_API_KEY2
hostname = "mqtt.thingspeak.com"
topic = 'channels/' + str(CHANNEL_ID0) + '/publish/' + WRITE_API_KEY0
payload = 'field1=' + str(CHANNEL_ID1) + '&field2=' + READ_API_KEY1
publish.single(topic, payload=payload, hostname=hostname)
print("Guardada info nuevo channel " + str(CHANNEL_ID1))
time.sleep(15)
payload = 'field1=' + str(CHANNEL_ID2) + '&field2=' + READ_API_KEY2
publish.single(topic, payload=payload, hostname=hostname)
print("Guardada info nuevo channel " + str(CHANNEL_ID2))
j = 0
# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # Ponemos la placa en modo BCM
GPIO.cleanup()
pin = 4

try:
    while True:
        ntime1 = float(time.clock())
        topic = topic1
        if j % 2 > 0:
            topic = topic2
        # leyendo el API accedemos a los metodos a utilizar
        data = []  # Definimos data como un array

        GPIO.setup(pin, GPIO.OUT)  # Configuramos el pin 4 como salida
        GPIO.output(pin, GPIO.HIGH)  # Enviamos una signal
        time.sleep(0.025)  # pausa
        GPIO.output(pin, GPIO.LOW)  # Cerramos la signal
        time.sleep(0.2)  # pausa

        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Ponemos el pin 4 en modo lectura

        for i in range(0, 500):  # Lee los bits que conforman la respuesta binaria del sensor
            data.append(GPIO.input(pin))
            # data.append(0)
        # Define algunas variables usadas para calculos mas adelante
        count = 0
        inicio = 0
        word = ""
        crc_check = 0
        retry = 0
        try:  # Hazlo mientras no existan errores, si detectas error salta a "except"
            # El siguiente codigo lee los bits de respuesta que envia el
            # sensor y los transforma a un numero decimal leible.
            # Buscamos el primer canto de bajada
            if retry == 0:
                inicio = data.index(0)
                #     flag = 0
            for senal in data[inicio:500]:
                 if senal == 1:
                     flag = 1
                     count = count + 1

                 if senal == 0 and flag == 1:
                     flag = 0
                     if count < 4:
                         word = word + "0"
                     else:
                         word = word + "1"
                     count = 0

            Humidity = bin2dec(word[0:8])
            Temperature = bin2dec(word[16:24])
            crc = bin2dec(word[32:40])
            
            j = j + 1
        except Exception:
            print "ERR_RANGE"
        else:
            crc_check = int(Humidity) + int(Temperature) - int(crc)
            payload = ""
            if 2 > crc_check > -2:  # La comprobacion del CRC se ha validado
                print "Humidity:" + str(Humidity) + " %"
                print "Temperature:" + str(Temperature) + " C"
                payload = 'field1=' + str(Temperature) + '&field2=' + str(Humidity)
                ntime2 = float(time.clock())
                retry = 0
            else:  # Si no es valido
                print "ERR_CRC (" + str(crc) + "): ERR_H (" + str(Humidity) + ") or ERR_T (" + str(Temperature) + ")"
                retry = 1
            # Publish a single message to a broker, then disconnect cleanly
            if payload != "":
                ntime2 = float(time.clock())
                ntime = 10.0 - ntime2 + ntime1
                if ntime > 0:
                    time.sleep(ntime)
                publish.single(topic, payload=payload, hostname=hostname, keepalive=120)

except KeyboardInterrupt:
    print("Salida por Ctrl+c. Finalizando ....")
    connTCP.close()
except socket.gaierror:
    print("Cancelacion por fallo en el publish MQTT ....")
    connTCP.close()



