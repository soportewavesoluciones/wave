import time
import math
from machine import ADC, Pin

class ZMPT101B:
    def __init__(self, pin, frequency, sensitivity=1.0):
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)
        self.adc.width(ADC.WIDTH_12BIT)
        self.period = 1_000_000 // frequency
        self.sensitivity = sensitivity
        self.VREF = 3.3
        self.ADC_SCALE = 4095

    def set_sensitivity(self, value):
        self.sensitivity = value

    def get_zero_point(self):
        Vsum = 0
        measurements_count = 0
        t_start = time.ticks_us()

        while time.ticks_diff(time.ticks_us(), t_start) < self.period:
            Vsum += self.adc.read()
            measurements_count += 1

        return Vsum // measurements_count

    def get_rms_voltage(self, loop_count=10):
        reading_voltage = 0.0

        for _ in range(loop_count):
            zero_point = self.get_zero_point()

            Vsum = 0
            measurements_count = 0
            t_start = time.ticks_us()

            while time.ticks_diff(time.ticks_us(), t_start) < self.period:
                Vnow = self.adc.read() - zero_point
                Vsum += Vnow ** 2
                measurements_count += 1

            rms = math.sqrt(Vsum / measurements_count)
            voltage = rms / self.ADC_SCALE * self.VREF * self.sensitivity
            reading_voltage += voltage

        return reading_voltage / loop_count
