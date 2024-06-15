from machine import Pin 
import time

red = Pin(26, Pin.OUT)
green = Pin(27, Pin.OUT)
blue = Pin(14, Pin.OUT)

def change_led_color(color):
    if color == "red":
        red.value(0)
        green.value(1)
        blue.value(1)
    if color == "green":
        red.value(1)
        green.value(0)
        blue.value(1)
    if color == "blue":
        red.value(1)
        green.value(1)
        blue.value(0)
    if color == "white":
        red.value(0)
        green.value(0)
        blue.value(0)
    if color == "":
        red.value(1)
        green.value(1)
        blue.value(1)

