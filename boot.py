import gc
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


def connect_wlan(ssid, password):
    """Connects build-in WLAN interface to the network.
    Args:
        ssid: Service name of Wi-Fi network.
        password: Password for that Wi-Fi network.
    Returns:
        True for success, Exception otherwise.
    """
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)
    sta_if.active(True)
    ap_if.active(False)

    if not sta_if.isconnected():
        print("Connecting to WLAN ({})...".format(ssid))
        sta_if.active(True)
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            pass

    return True


def main():
    """Main function. Runs after board boot, before main.py
    Connects to Wi-Fi and checks for latest OTA version.
    """
    gc.collect()
    gc.enable()

    #if __name__ == "__main__":
    demo()

    # Wi-Fi credentials
    print("Desde BOOT")
    connect_wlan(SSID, PASSWORD)


    import senko
    OTA = senko.Senko(user="soportewavesoluciones", repo="wave", working_dir="Viena_III", files=["main.py","boot.py","ble_ConfigNetwork.py"])

    if OTA.update():
        print("Updated to the latest version! Rebooting...")
        machine.reset()


if __name__ == "__main__":
    main()