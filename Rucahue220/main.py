from zmpt101b import ZMPT101B
from influx import INFLUX
import utime  # Módulo para funciones de tiempo en MicroPython


influx = INFLUX()

RETARDO = 60000 # Tiempo de ejecucion del programa
# Configuración de los pines y frecuencia
# Pines para las fases de servicio de red
service_pins = [36, 39, 34]  # GPIO36, GPIO39, GPIO34
# Pines para las fases del generador
generator_pins = [35, 32, 33]  # GPIO35, GPIO32, GPIO33

frequency = 50  # Frecuencia en Hz
sensitivity = 1045.0  # Sensibilidad configurada para todos los sensores

# Crear instancias de los sensores
service_sensors = [ZMPT101B(pin=pin, frequency=frequency, sensitivity=sensitivity) for pin in service_pins]
generator_sensors = [ZMPT101B(pin=pin, frequency=frequency, sensitivity=sensitivity) for pin in generator_pins]

# Función para leer los valores RMS de los sensores
def read_sensors(sensors, name):
    print(f"\nLecturas de {name}:")
    for i, sensor in enumerate(sensors):
        rms_voltage = sensor.get_rms_voltage(loop_count=10)
        print(f"Fase {i + 1} ({name}): {rms_voltage:.2f} V")
        # Enviar a InfluxDB
        field_name = f"{name}_Fase{i + 1}"  # Campo específico para cada fase
        influx.send_to_influxdb(field_name, rms_voltage)

# Lecturas continuas
def control(timer):
    try:
        # Leer los sensores del servicio de red
        read_sensors(service_sensors, "ServiciodeRed")

        # Leer los sensores del generador
        read_sensors(generator_sensors, "Generador")

        timer.init(period=RETARDO, mode=machine.Timer.PERIODIC, callback=control)

    except Exception as e:
        print("Error al enviar datos a InfluxDB:", e)
        machine.reset()


 # Iniciar el temporizador
timer = machine.Timer(-1)
# Inicializar el temporizador para que se ejecute por primera vez después del retardo
timer.init(period=RETARDO, mode=machine.Timer.ONE_SHOT, callback=control)
