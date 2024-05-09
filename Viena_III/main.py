import network
import time
import json
import urequests as requests
import random
import bluetooth
from ble_ConfigNetwork import BLESimplePeripheral
from ble_ConfigNetwork import demo
import machine
from machine import Pin 
from machine import SoftI2C
#import vl53l1x
#from lidar import LIDAR


# TF-Luna has the default slave_address 0x10
#LIDAR_ADDRESS = 0x10
#i2c= SoftI2C(scl=Pin(22), sda=Pin(21), freq=115200, timeout=2500)
#lidar = LIDAR(i2c, LIDAR_ADDRESS)

# VL53l1x
#i2c= SoftI2C(scl=Pin(22), sda=Pin(21), freq=115200, timeout=2500)
#tof= vl53l1x.VL53L1X(i2c)

#Nominate a trigger pin on ESP8266 and declare it as an output pin
trigger = machine.Pin((5), machine.Pin.OUT)

#Nominate an echo pin and declare it as an input pin
echo = machine.Pin((18), machine.Pin.IN)


# Función para cargar la configuración desde un archivo JSON
def cargar_configuracion(nombre_archivo):
    with open(nombre_archivo, 'r') as f:
        config = json.load(f)
    return config

# Obtener los valores de la configuración
config = cargar_configuracion('config.json')

# Obtener los valores de la configuración
SSID = config['ssid']
PASSWORD = config['password']
DEVICE = config['device']
HEIGHTSENSOR = config['heightSensor']
HEIGHTTANK = config['heightTank']
VOLUMETANK = config['volumeTank']
BUCKET = config['bucket']
TOKEN = config['token']
ORG = config['org']
INFLUXDB_URL = config['influxdb_url']
MEASUREMENT = config['measurement']
RETARDO = config['retardo']  # Intervalo de tiempo entre las lecturas
FIELDA = config['FIELDA']  # Nombre del primer field
FIELDB = config['FIELDB']  # Nombre del segundo field para el valor aleatorio
FIELDC = config['FIELDC']  # Nombre del segundo field para el valor aleatorio

# Conecta a la red Wi-Fi
def connect_wifi(ssid, password):
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("Conectando a la red Wi-Fi...")
        sta_if.active(True)
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            pass
    print("Conexión Wi-Fi exitosa.")
    print("Dirección IP:", sta_if.ifconfig()[0])

def convert():
    import utime
    trigger.value(1)
    utime.sleep(2)
    #Set the trigger high for 15 microseconds
    trigger.value(0)
    utime.sleep_us(15)
    trigger.value(1)
    #Set a timer to monitor the echo pin for a couple of seconds
    pulse = machine.time_pulse_us(echo,1)
    #Calculate the distance to the surface based on the speed of sound.
    distance = (pulse/1000000)*34000/2
    hH2O=float(HEIGHTSENSOR)-distance
    return hH2O

# Función para leer el estado de la entrada digital
def read_inputA():
    levelh=convert()
    return levelh

# Función para generar un valor aleatorio entre 0 y 1
def read_inputB():
    levelp = ((convert()*100/float(HEIGHTTANK))) 
    # VL53l1x
    #tof.start()
    #lectura=tof.read()
    #tof.stop()
    #return lidar.distance()
    #num_list = [0, 100, 200, 300, 400, 500]
    #Set and hold the trigger low.
    return levelp

# Función para leer el estado de la entrada digital
def read_inputC():
    levelc = (((convert()/float(HEIGHTTANK))*float(VOLUMETANK)))
    return levelc


# Función para enviar datos a InfluxDB
def send_to_influxdb(valueA, valueB, valueC):
    data = "{},device={} {}={},{}={},{}={}".format(MEASUREMENT, DEVICE, FIELDA, valueA, FIELDB, valueB, FIELDC, valueC)
    headers = {
        "Authorization": "Token {}".format(TOKEN),
        "Content-Type": "text/plain"
    }
    url = "{}/api/v2/write?org={}&bucket={}&precision=s".format(INFLUXDB_URL, ORG, BUCKET)
    response = requests.post(url, data=data, headers=headers)
    print("Solicitud POST completa:")
    print("URL:", url)
    print("Headers:", headers)
    print("Data:", data)
    print("Respuesta del servidor:", response.text)


#if __name__ == "__main__":
#    demo()

# Conectar a la red Wi-Fi
connect_wifi(SSID, PASSWORD)

# Función a ejecutar después de cierto tiempo

def enviar_datos(timer):
    valueA = read_inputA()
    valueB = read_inputB()
    valueC = read_inputC()
    send_to_influxdb(valueA, valueB, valueC)
    timer.init(period=RETARDO, mode=machine.Timer.PERIODIC, callback=enviar_datos)

# Iniciar el temporizador
timer = machine.Timer(-1)
# Inicializar el temporizador para que se ejecute por primera vez después del retardo
timer.init(period=RETARDO, mode=machine.Timer.ONE_SHOT, callback=enviar_datos)
