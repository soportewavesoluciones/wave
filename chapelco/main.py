import network
import time
import json
import urequests as requests
import bluetooth
from ble_ConfigNetwork import BLESimplePeripheral
from ble_ConfigNetwork import demo
import machine
from machine import Pin 
import rgb
import gc
import os
import utime  # Importa utime una vez al principio

# Nominate a trigger pin on ESP8266 and declare it as an output pin
trigger = machine.Pin(5, machine.Pin.OUT)

# Nominate an echo pin and declare it as an input pin
echo = machine.Pin(18, machine.Pin.IN)

# Función para cargar la configuración desde un archivo JSON
def cargar_configuracion(nombre_archivo):
    with open(nombre_archivo, 'r') as f:
        config = json.load(f)
    return config

# Obtener los valores de la configuración
config = cargar_configuracion('config.json')
influx = cargar_configuracion('influx.json')

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
FIELDC = config['FIELDC']  # Nombre del tercer field
FIELDD = config['FIELDD']  # Nombre del cuarto field

# Conecta a la red Wi-Fi
def connect_wifi(ssid, password, max_retries=10):
    sta_if = network.WLAN(network.STA_IF)
    if sta_if.isconnected():
        print("Ya conectado a la red Wi-Fi.")
        print("Dirección IP:", sta_if.ifconfig()[0])
        rgb.change_led_color("green")
        return True
    
    print("Conectando a la red Wi-Fi...")
    rgb.change_led_color("white")
    sta_if.active(True)
    
    retry_count = 0
    while not sta_if.isconnected() and retry_count < max_retries:
        if sta_if.status() == network.STAT_CONNECTING:
            print("Wi-Fi está conectando, esperando...")
            time.sleep(5)
            continue
        
        sta_if.disconnect()
        sta_if.connect(ssid, password)
        
        print("Intento de conexión #{}...".format(retry_count + 1))
        time.sleep(5)  # Esperar 5 segundos antes de intentar reconectar
        retry_count += 1
    
    if not sta_if.isconnected():
        print("No se pudo conectar a la red Wi-Fi después de {} intentos.".format(max_retries))
        rgb.change_led_color("red")
        return False
    else:
        print("Conexión Wi-Fi exitosa.")
        print("Dirección IP:", sta_if.ifconfig()[0])
        rgb.change_led_color("green")
        return True

def medir():
    total = 0

    for i in range(21):
        trigger.value(1)
        utime.sleep_ms(50)
        trigger.value(0)
        utime.sleep_us(10)
        trigger.value(1)
        pulse = machine.time_pulse_us(echo, 1)
        distance = (pulse / 1000000) * 34000 / 2
        if distance > 500 or distance < 25:
            distance = 0
        total += distance
    
    MEDICION = total / 20
    
    levelh = float(HEIGHTSENSOR) - MEDICION  
    levelc = ((levelh / float(HEIGHTTANK)) * float(VOLUMETANK))
    levelp = ((levelh * 100 / float(HEIGHTTANK)))

    return {
        "levelh": levelh,
        "levelc": levelc,
        "levelp": levelp,
        "medicion": MEDICION
    }

# Función para enviar datos a InfluxDB
def send_to_influxdb(valueA, valueB, valueC, valueD):
    data = "{},device={} {}={},{}={},{}={},{}={}".format(MEASUREMENT, DEVICE, FIELDA, valueA, FIELDB, valueB, FIELDC, valueC, FIELDD, valueD)
    headers = {
        "Authorization": "Token {}".format(TOKEN),
        "Content-Type": "text/plain"
    }
    url = "{}/api/v2/write?org={}&bucket={}&precision=s".format(INFLUXDB_URL, ORG, BUCKET)
    response = None
    try:
        response = requests.post(url, data=data, headers=headers)
        print("Solicitud POST completa:")
        print("Data:", data)
        print("Respuesta del servidor:", response.status_code)
        
        if response.status_code == 204: 
            rgb.change_led_color("green")
        else:
            rgb.change_led_color("red")
    except Exception as e:
        print("Error al enviar datos a InfluxDB:", e)
        rgb.change_led_color("red")
    finally:
        if response is not None:
            response.close()  # Cerrar la respuesta para liberar memoria
        gc.collect()

# Función a ejecutar después de cierto tiempo
def enviar_datos(timer):
    try:
        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
            print("Wi-Fi desconectado. Intentando reconectar...")
            sta_if.active(False)
            time.sleep(2)
            if not connect_wifi(SSID, PASSWORD):
                print("No se pudo reconectar. Reiniciando...")
                machine.reset()
        rgb.change_led_color("blue")
        valores = medir()
        levelh = valores["levelh"]
        levelp = valores["levelp"]
        levelc = valores["levelc"]
        rawData = valores["medicion"]
        send_to_influxdb(levelh, levelp, levelc, rawData)
        timer.init(period=RETARDO, mode=machine.Timer.PERIODIC, callback=enviar_datos)
    except OSError as e:
        if e.args[0] == 12:  # Comprueba si el código de error es ENOMEM
            print("Error de memoria. Reiniciando ESP32...")
            machine.reset()  # Reinicia el ESP32
        else:
            print(e)
            machine.reset()

# Iniciar el temporizador
timer = machine.Timer(-1)
# Inicializar el temporizador para que se ejecute por primera vez después del retardo
timer.init(period=RETARDO, mode=machine.Timer.ONE_SHOT, callback=enviar_datos)

