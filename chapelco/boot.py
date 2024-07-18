import gc
import network
import time
import json
import urequests as requests
import bluetooth
from ble_ConfigNetwork import BLESimplePeripheral, demo
import machine
import rgb
import senko
import _thread
import threading

rgb.change_led_color("white")

# Evento para controlar el parpadeo del LED
stop_blinking_event = threading.Event()

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

def connect_wlan(ssid, password):
    """Connects built-in WLAN interface to the network."""
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)
    sta_if.active(True)
    ap_if.active(False)

    if not sta_if.isconnected():
        print("Connecting to WLAN ({})...".format(ssid))
        sta_if.connect(ssid, password)
        retry_count = 0
        while not sta_if.isconnected() and retry_count < 10:
            time.sleep(1)
            retry_count += 1
            print("Retrying connection to WLAN... ({})".format(retry_count))
        if not sta_if.isconnected():
            print("Failed to connect to WLAN.")
            rgb.change_led_color("red")
            return False
        print("Connected!")
        rgb.change_led_color("green")
    return True

def led_blink(stop_event):
    """Makes the LED blink to indicate OTA update process."""
    while not stop_event.is_set():
        rgb.change_led_color("blue")
        time.sleep(0.5)
        rgb.change_led_color("")
        time.sleep(0.5)
    rgb.change_led_color("green")  # Set the LED to green after stopping the blink

def main():
    """Main function. Runs after board boot, before main.py."""
    gc.collect()
    gc.enable()

    demo()

    # Wi-Fi credentials
    print("Desde BOOT")
    if not connect_wlan(SSID, PASSWORD):
        print("Failed to connect to Wi-Fi. Rebooting...")
        machine.reset()

    OTA = senko.Senko(user="soportewavesoluciones", repo="wave", working_dir="chapelco", files=["main.py", "boot.py", "ble_ConfigNetwork.py", "config.json"])

    try:
        print("Checking for OTA update...")
        # Start LED blinking in a separate thread
        blink_thread = threading.Thread(target=led_blink, args=(stop_blinking_event,))
        blink_thread.start()
        
        if OTA.update():
            print("Updated to the latest version! Rebooting...")
            machine.reset()
    except Exception as e:
        print("An error occurred during the OTA update:", e)
    finally:
        # Stop LED blinking and set it to a stable color after OTA update check
        print("OTA finally")
        stop_blinking_event.set()
        blink_thread.join()  # Wait for the blink_thread to finish
        rgb.change_led_color("green")

if __name__ == "__main__":
    main()
