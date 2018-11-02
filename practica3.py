import RPi.GPIO as gpio
import Adafruit_ADS1x15 as analogo
import time
from firebase import firebase
import threading
from RPLCD.i2c import CharLCD


gpio.setwarnings(False)
gpio.setmode(gpio.BOARD)
db = firebase.FirebaseApplication('https://practica3-sd.firebaseio.com', None)

def call(c):
    """Cambia el valor de on/off"""
    global on    
    on = not on

# Declaraciones de objetos y constantes
lcd = CharLCD('PCF8574', 0x27)
adc = analogo.ADS1115()
GAIN = 1
maximaLuz = 26500

#Pines
pir = 11
interruptor = 35
ledVentilacion = 13
ledIluminacion = 15
ledSistema = 19

#Setup
gpio.setup(pir, gpio.IN, pull_up_down = gpio.PUD_DOWN)
gpio.setup(interruptor, gpio.IN)
gpio.setup(ledVentilacion, gpio.OUT)
gpio.setup(ledIluminacion, gpio.OUT)
gpio.setup(ledSistema, gpio.OUT)

#Eventos
gpio.add_event_detect(interruptor, gpio.RISING, callback = call, bouncetime  = 300)

#Variables de tiempo de ejecucin
limiteIluminacion = 0
limiteTemperatura = 0
estadoUPS = False
on = 1

def getIluminacion():
    """Obtiene el porcentaje de iluminacin"""
    value = adc.read_adc(0, gain=GAIN)
    percent = (100 * value) / maximaLuz    
    return round(percent, 2)

def getTemperatura():
    """Obtiene la temperatura del ambiente"""
    file = open('/sys/bus/w1/devices/28-000d98430467/w1_slave')
    lines = file.readlines()
    temperatureLine = lines[1]
    temp = float(temperatureLine.split('=')[1]) / 1000
    return round(temp, 2)

def getMovimiento():
    """Obtiene un valor booleano de si hay presencia en la biblioteca"""
    return gpio.input(pir)

def getLimites():
    """Obtiene los datos desde firebase"""    
    while True:
        global limiteIluminacion
        global limiteTemperatura
        global estadoUPS
        data = db.get('/limites', None)
        limiteTemperatura = data['temperatura']
        limiteIluminacion = data['iluminacion']
        estadoUPS = data['ups']        

def apagar():
    """Apaga todos los leds y el lcd"""
    lcd.clear()
    gpio.output(ledVentilacion, 0)
    gpio.output(ledIluminacion, 0)
    gpio.output(ledSistema, 0)
    print("El sistema está apagado")
    print("")

def write(t, i):
    """Da salida a los datos de temperatura e iluminación"""
    lcd.clear()
    lcd.cursor_pos = (0, 0)
    lcd.write_string("Temp: " + str(t) + " °C")
##    print("Temp: " + str(t) + " °C")
    lcd.cursor_pos = (1, 0)
    lcd.write_string("Ilum: " + str(i) + "%")
##    print("Ilum: " + str(i) + "%")
    print("")

def main():
    """Proceso principal de la aplicación"""    
    global limiteIluminacion
    global limiteTemperatura
    global estadoUPS
    global on
    global interruptor
    global pir
    global ledSistema
    global ledVentilacion
    global ledIluminacion
    
    #función ventilador S * P * T * (U * I)'
    #función luz S * P * I
    
    # Variables de decisión
    p = gpio.input(pir)
    u = estadoUPS
    i = getIluminacion() < limiteIluminacion
    t = getTemperatura() > limiteTemperatura
    
    print("SYS: ", on)
    print("PIR: ", p)
    print("UPS: ", u)
    print("OSCURO: ", i)
    print("CALOR: ", t)
    
    if on:
        write(getTemperatura(), getIluminacion())
        gpio.output(ledSistema, 1)
        #Temperatura
        if (p & t & ~(u & i)):
            gpio.output(ledVentilacion, 1)
        else:
            gpio.output(ledVentilacion, 0)

        #Iluminación
        if(p & i):
            gpio.output(ledIluminacion, 1)
        else:
            gpio.output(ledIluminacion, 0)
    else:
        apagar()    

#Hilos
dataThread = threading.Thread(target=getLimites)
dataThread.start()

try:
    while True:
        main()
except KeyboardInterrupt:    
    print("FIN")
