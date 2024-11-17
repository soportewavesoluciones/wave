import time
import json
import urequests as requests
import machine

class INFLUX:
    def __init__(self):
        self.BUCKET = "Power220"
        self.TOKEN = ""
        self.ORG = ""
        self.INFLUXDB_URL = ""
        self.MEASUREMENT = "Power_status"
        self.DEVICE= "Rucahue"

# Función para enviar datos a InfluxDB
    def send_to_influxdb(self, FIELDB, valueB):
        try:
            data = "{},device={} {}={}".format(self.MEASUREMENT, self.DEVICE, FIELDB, valueB )
            headers = {
                "Authorization": "Token {}".format(self.TOKEN),
                "Content-Type": "text/plain"
            }
            url = "{}/api/v2/write?org={}&bucket={}&precision=s".format(self.INFLUXDB_URL, self.ORG, self.BUCKET)
            response = requests.post(url, data=data, headers=headers)
            print("Solicitud POST completa:")
            print("URL:", url)
            print("Headers:", headers)
            print("Data:", data)
            print("Respuesta del servidor:", response.text)
        except Exception as e:
            print("Error al enviar datos a InfluxDB:", e)
            machine.reset()
