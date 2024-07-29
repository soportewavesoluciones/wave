import network
import time
import json
import urequests as requests
import machine
from machine import Pin 
import gc
import os


SSID = "cotemax_77d"
PASSWORD = "XXX"
BUCKET = "BUCKET_1"
TOKEN = "XXX"
ORG = "XXX"
INFLUXDB_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
MEASUREMENT = "Level_status"
MEASUREMENTP = "Pump_status"
FIELDA = "levelh"
DEVICE= "Chacra30"
FIELDB = "pumpsta"
NIVEL_MAX = 280
NIVEL_MIN = 200
TIEMPO_MAXIMO_FUNCIONAMIENTO = 100  # Tiempo máximo en minutos
TIEMPO_NIVEL_SIN_SUBIR_MAX = 100  # Tiempo máximo que la bomba puede estar encendida sin que el nivel suba en minutos
RETARDO = 60000 # Tiempo de ejecucion del programa



# Variables globales
ESTADO_BOMBA = 0  # 0: apagada, 1: encendida
TIEMPO_INICIO_BOMBA = None  # Tiempo de inicio de la bomba
ULTIMO_NIVEL = None  # Último nivel de agua registrado
TIEMPO_SIN_SUBIR = None  # Tiempo durante el cual el nivel no ha subido

# Salida rele
relay = Pin(5, Pin.OUT)
relay.value(1)


# Conecta a la red Wi-Fi
def connect_wifi(ssid, password):
    try:
        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
            print("Conectando a la red Wi-Fi...")
            sta_if.active(True)
            sta_if.connect(ssid, password)
            while not sta_if.isconnected():
                pass
        print("Conexión Wi-Fi exitosa.")
        print("Dirección IP:", sta_if.ifconfig()[0])
    except Exception as e:
        print("Error al enviar datos a InfluxDB:", e)
        machine.reset()

#Leer Influx
def read_from_influxdb():
    try:
        query = 'from(bucket: "{}") |> range(start: -1m) |> filter(fn: (r) => r._measurement == "{}" and r.device == "{}") |> filter(fn: (r) => r._field == "{}") |> group(columns: ["_measurement"]) |> mean(column: "_value")'.format(BUCKET, MEASUREMENT, DEVICE, FIELDA)
        url = "{}/api/v2/query?org={}".format(INFLUXDB_URL, ORG)
        headers = {
            "Authorization": "Token {}".format(TOKEN),
            "Content-Type": "application/vnd.flux",
            "Accept": "application/csv",
        }
        data = query.strip()  # Aseguramos que la consulta esté formateada correctamente

        response = requests.post(url, headers=headers, data=data)

        #print("URL de consulta:", url)
        #print("Headers:", headers)
        #print("Data:", data)
        #print("Respuesta del servidor (raw):", response.text)
        # Obtenemos el contenido de la respuesta como texto
        response_text = response.text

        # Dividimos la respuesta en líneas
        lines = response_text.split('\n')

        # Buscamos la línea que contiene el valor promedio
        for line in lines:
            if 'Level_status' in line:
                # Dividimos la línea por comas y tomamos el último valor (el promedio)
                columns = line.split(',')
                nivel_promedio = float(columns[-1])

        #print("El nivel promedio es:", nivel_promedio)
        return nivel_promedio
    except Exception as e:
        print("Error al enviar datos a InfluxDB:", e)
        machine.reset()

# Función para controlar la bomba según el nivel de agua y el tiempo máximo de funcionamiento
def controlar_bomba(nivel_actual, NIVEL_MAX, NIVEL_MIN, TIEMPO_MAXIMO_FUNCIONAMIENTO, TIEMPO_NIVEL_SIN_SUBIR_MAX):
    global ESTADO_BOMBA, TIEMPO_INICIO_BOMBA, ULTIMO_NIVEL, TIEMPO_SIN_SUBIR

    # Verificar si la bomba estaba encendida antes de apagarse
    if ESTADO_BOMBA == 1:
        tiempo_actual = time.time()
        tiempo_funcionamiento_bomba = (tiempo_actual - TIEMPO_INICIO_BOMBA) / 60  # Convertir segundos a minutos

        # Verificar si el nivel ha subido
        if nivel_actual > ULTIMO_NIVEL:
            TIEMPO_SIN_SUBIR = None  # Reiniciar el tiempo sin subir
        else:
            if TIEMPO_SIN_SUBIR is None:
                TIEMPO_SIN_SUBIR = tiempo_actual
            tiempo_sin_subir = (tiempo_actual - TIEMPO_SIN_SUBIR) / 60  # Convertir segundos a minutos
            if tiempo_sin_subir >= TIEMPO_NIVEL_SIN_SUBIR_MAX:
                ESTADO_BOMBA = 0  # Apagar la bomba para evitar daños
                TIEMPO_INICIO_BOMBA = None  # Reiniciar el tiempo de inicio
                ULTIMO_NIVEL = None  # Reiniciar el último nivel
                TIEMPO_SIN_SUBIR = None  # Reiniciar el tiempo sin subir
                return 0

        if tiempo_funcionamiento_bomba >= TIEMPO_MAXIMO_FUNCIONAMIENTO:
            ESTADO_BOMBA = 0  # Apagar la bomba si ha alcanzado el tiempo máximo de funcionamiento
            TIEMPO_INICIO_BOMBA = None  # Reiniciar el tiempo de inicio
            ULTIMO_NIVEL = None  # Reiniciar el último nivel
            TIEMPO_SIN_SUBIR = None  # Reiniciar el tiempo sin subir
            return 0

    # Controlar la bomba según los niveles de agua
    if nivel_actual >= NIVEL_MAX:
        ESTADO_BOMBA = 0  # Apagar la bomba
        TIEMPO_INICIO_BOMBA = None  # Reiniciar el tiempo de inicio
        ULTIMO_NIVEL = None  # Reiniciar el último nivel
        TIEMPO_SIN_SUBIR = None  # Reiniciar el tiempo sin subir
    elif nivel_actual <= NIVEL_MIN and (TIEMPO_INICIO_BOMBA is None or tiempo_funcionamiento_bomba < TIEMPO_MAXIMO_FUNCIONAMIENTO):
        if ESTADO_BOMBA == 0:
            TIEMPO_INICIO_BOMBA = time.time()  # Registrar el tiempo de inicio
        ESTADO_BOMBA = 1  # Encender la bomba

    ULTIMO_NIVEL = nivel_actual  # Actualizar el último nivel registrado
    return ESTADO_BOMBA

# Función para enviar datos a InfluxDB
def send_to_influxdb(valueB):
    try:
        data = "{},device={} {}={}".format(MEASUREMENTP, DEVICE, FIELDB, valueB )
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
    except Exception as e:
        print("Error al enviar datos a InfluxDB:", e)
        machine.reset()

# Conectar a la red Wi-Fi
connect_wifi(SSID, PASSWORD)

def control(timer):
    #Traer valor de influx
    nivel_actual = read_from_influxdb()

    #Controlar bomba
    estado_bomba = controlar_bomba(nivel_actual, NIVEL_MAX, NIVEL_MIN, TIEMPO_MAXIMO_FUNCIONAMIENTO, TIEMPO_NIVEL_SIN_SUBIR_MAX)

    #Enviar a influx el estado
    send_to_influxdb(estado_bomba)

    if estado_bomba == 0:
        print("La bomba está apagada")
        relay.value(1)
    elif estado_bomba == 1:
        print("La bomba está encendida")
        relay.value(0)
    else:
        print("La bomba mantiene su estado actual")

    timer.init(period=RETARDO, mode=machine.Timer.PERIODIC, callback=control)

# Iniciar el temporizador
timer = machine.Timer(-1)
# Inicializar el temporizador para que se ejecute por primera vez después del retardo
timer.init(period=RETARDO, mode=machine.Timer.ONE_SHOT, callback=control)