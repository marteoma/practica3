import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BOARD)

ledVentilacion = 13
ledIluminacion = 15
ledSistema = 19
interruptor = 35
pir = 11
#Setup
gpio.setup(ledVentilacion, gpio.OUT)
gpio.setup(ledIluminacion, gpio.OUT)
gpio.setup(ledSistema, gpio.OUT)
gpio.setup(interruptor, gpio.IN)
gpio.setup(pir, gpio.IN, pull_up_down = gpio.PUD_DOWN)

while True:
    print(gpio.input(pir))
    time.sleep(.5)
    
