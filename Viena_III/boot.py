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
import rgb

rgb.change_led_color("white")

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
        print("Connected!")
        rgb.change_led_color("green")
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
    OTA = senko.Senko(user="soportewavesoluciones", repo="wave", working_dir="Viena_III", files=["main.py","boot.py","ble_ConfigNetwork.py","config.json"])

    try:
        if OTA.update():
            print("Updated to the latest version! Rebooting...")
            machine.reset()
    except Exception as e:
        print("An error occurred during the OTA update:", e)


if __name__ == "__main__":
    main()
