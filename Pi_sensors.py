# encoding = utf8
"""
@author:Jabi Martin
@desc: Obtiene %CPU y %RAM
"""
import paho.mqtt.publish as publish
import time
import httplib
import urllib
import json
import RPi.GPIO as GPIO   # Importamos las librerias necesarias para usar los pines GPIO


def bin2dec(string_num):  # Creamos una funcion para transformar de binario a decimal
    return str(int(string_num, 2))


USER_API_KEY = "9TNQC2RGM3Q0L07A"
# Establecer conexion TCP
server = "api.thingspeak.com"
connTCP = httplib.HTTPSConnection(server)
print("Estableciendo conexion con " + server)
connTCP.connect()
print("Conexion establecida")

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
print("Enviando Crear Canal 1...")
connTCP.request(method, relative_uri, body=payload_encode, headers=headers)
print("Enviada Peticion de creaccion de canal nuevo")
respuesta = connTCP.getresponse()
status = respuesta.status
print(str(status))
contenido = respuesta.read()
# print(contenido)
contenido_json = json.loads(contenido)
CHANNEL_ID1 = contenido_json['id']
WRITE_API_KEY1 = contenido_json['api_keys'][0]['api_key']
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


# Replace <channelID> with the channel ID
# Replace <apikey> with the WRITE_API_KEY
topic1 = 'channels/' + CHANNEL_ID1 + '/publish/' + WRITE_API_KEY1
topic2 = 'channels/' + CHANNEL_ID2 + '/publish/' + WRITE_API_KEY2
hostname = "mqtt.thingspeak.com"
i = 0
# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # Ponemos la placa en modo BCM
GPIO.cleanup()
pin = 4

try:
    while True:
        ntime1 = float(time.clock())
        topic = topic1
        if i % 2 > 0:
            topic = topic2

        # leyendo el API accedemos a los metodos a utilizar
        data = []  # Definimos data como un array

        GPIO.setup(pin, GPIO.OUT)  # Configuramos el pin 4 como salida
        GPIO.output(pin, GPIO.HIGH)  # Enviamos una señal
        time.sleep(0.025)  # Pequeña pausa
        GPIO.output(pin, GPIO.LOW)  # Cerramos la señal
        time.sleep(0.2)  # Pequeña pausa

        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Ponemos el pin 4 en modo lectura

        for i in range(0, 500):  # Lee los bits que conforman la respuesta binaria del sensor
            data.append(GPIO.input(pin))
        # Define algunas variables usadas para cálculos más adelante
        count = 0
        inicio = 0
        word = ""
        crc_check = 0
        retry = 0
        try:  # Hazlo mientras no existan errores, si detectas error salta a "except"
            # El siguiente código lee los bits de respuesta que envia el
            # sensor y los transforma a un número decimal leible.
            # Buscamos el primer canto de bajada
            if retry == 0:
                inicio = data.index(0)

            flag = 0
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
            else:  # Si no es válido
                print "ERR_CRC (" + str(crc) + "): ERR_H (" + str(Humidity) + ") or ERR_T (" + str(Temperature) + ")"
                retry = 1
            # Publish a single message to a broker, then disconnect cleanly
            if payload != "":
                ntime2 = float(time.clock())
                ntime = 10.0 - ntime2 + ntime1
                if ntime > 0:
                    time.sleep(ntime)
                publish.single(topic, payload=payload, hostname=hostname)
except KeyboardInterrupt:
    print("Salida por Ctrl+c. Finalizando ....")


