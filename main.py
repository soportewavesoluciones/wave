import network
import time
import json
import urequests as requests
import random
import bluetooth
from ble_ConfigNetwork import BLESimplePeripheral
from ble_ConfigNetwork import demo
import machine



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
DISPOSITIVO = config['dispositivo']
BUCKET = config['bucket']
TOKEN = config['token']
ORG = config['org']
INFLUXDB_URL = config['influxdb_url']
MEASUREMENT = config['measurement']
RETARDO = config['retardo']  # Intervalo de tiempo entre las lecturas
FIELDA = config['FIELDA']  # Nombre del primer field
FIELDB = config['FIELDB']  # Nombre del segundo field para el valor aleatorio

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



# Función para leer el estado de la entrada digital
def read_inputA():
    num_list = [0, 1, 2, 3, 4, 5]
    return random.choice(num_list)

# Función para generar un valor aleatorio entre 0 y 1
def read_inputB():
    return random.randint(0, 1)

# Función para enviar datos a InfluxDB
def send_to_influxdb(valueA, valueB):
    data = "{},dispositivo={} {}={},{}={}".format(MEASUREMENT, DISPOSITIVO, FIELDA, valueA, FIELDB, valueB)
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


if __name__ == "__main__":
    demo()

# Conectar a la red Wi-Fi
connect_wifi(SSID, PASSWORD)

# Función a ejecutar después de cierto tiempo
def enviar_datos(timer):
    valueA = read_inputA()
    valueB = read_inputB()
    send_to_influxdb(valueA, valueB)
    timer.init(period=RETARDO, mode=machine.Timer.PERIODIC, callback=enviar_datos)

# Iniciar el temporizador
timer = machine.Timer(-1)
timer.init(period=RETARDO, mode=machine.Timer.PERIODIC, callback=enviar_datos)
