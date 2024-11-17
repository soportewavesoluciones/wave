import network
import time
import json
import urequests as requests
import machine
from machine import Pin 
import gc
import os

SSID = ""
PASSWORD = ""

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

# Conectar a la red Wi-Fi
connect_wifi(SSID, PASSWORD)
