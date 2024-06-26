import network
import time
import json
import urequests as requests
import bluetooth
from ble_ConfigNetwork import BLESimplePeripheral
from ble_ConfigNetwork import demo
import machine
from machine import Pin 
from machine import SoftI2C
from lidar import LIDAR
import rgb
import gc
import os

# TF-Luna has the default slave_address 0x10
LIDAR_ADDRESS = 0x10
i2c= SoftI2C(scl=Pin(22), sda=Pin(21), freq=115200, timeout=2500)
lidar = LIDAR(i2c, LIDAR_ADDRESS)

# Función para cargar la configuración desde un archivo JSON
def cargar_configuracion(nombre_archivo):
    with open(nombre_archivo, 'r') as f:
        config = json.load(f)
    return config

# Obtener los valores de la configuración
config = cargar_configuracion('config.json')

influx = cargar_configuracion('influx.json')
# Obtener los valores de la configuración
SSID = config['ssid']
PASSWORD = config['password']
DEVICE = config['device']
HEIGHTSENSOR = config['heightSensor']
HEIGHTTANK = config['heightTank']
VOLUMETANK = config['volumeTank']
BUCKET = config['bucket']
TOKEN = influx['token']
ORG = influx['org']
INFLUXDB_URL = influx['influxdb_url']
MEASUREMENT = config['measurement']
RETARDO = config['retardo']  # Intervalo de tiempo entre las lecturas
FIELDA = config['FIELDA']  # Nombre del primer field
FIELDB = config['FIELDB']  # Nombre del segundo field para el valor aleatorio
FIELDC = config['FIELDC']  # Nombre del segundo field para el valor aleatorio
FIELDD = config['FIELDD']
FIELDE = config['FIELDE']

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
    rgb.change_led_color("green")

def convert():
    hH2O=float(HEIGHTSENSOR)-lidar.distance()
    return hH2O

# Función para leer la altura del agua
def read_levelh():
    return convert()

# Función para generar un valor aleatorio entre 0 y 1
def read_levelp():
    levelp = ((convert()*100/float(HEIGHTTANK))) 
    return levelp

# Función para leer el estado de la entrada digital
def read_levelc():
    levelc = (((convert()/float(HEIGHTTANK))*float(VOLUMETANK)))
    return levelc

def read_distance():
    return lidar.distance()

def read_amp():
    return lidar.signal_amp()


# Función para enviar datos a InfluxDB
def send_to_influxdb(valueA, valueB, valueC, valueD, valueE):
    
    data = "{},device={} {}={},{}={},{}={},{}={},{}={}".format(MEASUREMENT, DEVICE, FIELDA, valueA, FIELDB, valueB, FIELDC, valueC, FIELDD, valueD, FIELDE, valueE)
    headers = {
        "Authorization": "Token {}".format(TOKEN),
        "Content-Type": "text/plain"
    }
    url = "{}/api/v2/write?org={}&bucket={}&precision=s".format(INFLUXDB_URL, ORG, BUCKET)
    response = requests.post(url, data=data, headers=headers)
    print("Solicitud POST completa:")
    print("Data:", data)
    print("Respuesta del servidor:", response.status_code)
       
    if response.status_code == 204: 
        rgb.change_led_color("green")
    else:
        rgb.change_led_color("red")
    gc.collect()


#if __name__ == "__main__":
#    demo()

# Conectar a la red Wi-Fi
connect_wifi(SSID, PASSWORD)

# Función a ejecutar después de cierto tiempo

def enviar_datos(timer):
    try:
        rgb.change_led_color("blue")
        levelh = read_levelh()
        levelp = read_levelp()
        levelc = read_levelc()
        rawData = read_distance()
        amp = read_amp()
        send_to_influxdb(levelh, levelp, levelc, rawData, amp)
        timer.init(period=RETARDO, mode=machine.Timer.PERIODIC, callback=enviar_datos)
    except OSError as e:
        if e.args[0] == 12:  # Comprueba si el código de error es ENOMEM
            print("Error de memoria. Reiniciando ESP32...")
            machine.reset()  # Reinicia el ESP32
        else: 
            print(e)
            machine.reset()  # Reinicia el ESP32
# Iniciar el temporizador
timer = machine.Timer(-1)
# Inicializar el temporizador para que se ejecute por primera vez después del retardo
timer.init(period=RETARDO, mode=machine.Timer.ONE_SHOT, callback=enviar_datos)
