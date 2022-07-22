import Adafruit_DHT
from gpiozero import Button
from gpiozero import LED
import AC_Encoder as AC_Controler
import os

#  Archivo destinado al control del hardware instaldo en la Raspberry

sensor = Adafruit_DHT.DHT11
pin = 2
btn = Button(27)
led = LED(24)


def Set_Led(State): 
    if State=='ON':
        led.on()
    else:
        led.off()
 
# pressed y released son funciones disparadas por los eventos respectivos sobre una entrada GPIO declarada (btn)
def pressed():
    os.environ["Power"]='ENCENDIDO' # variable de hambiente, delcara el estado del pin GPIO a todo el hambiente de trabajo 
    if AC_Controler.Send_Command():
        print('AIRE ACONDICIONADO ENCENDIDO')

def released():
    os.environ["Power"]='APAGADO' # variable de hambiente, delcara el estado del pin GPIO a todo el hambiente de trabajo 
    print('CORTE DE CORRIENTE ELECTRICA...')
    

# El senror DHT11  es medido pro esta funcion a partir de la libreria de Adafruit_DHT
# La funcion devuelve una bandera de fiabilidad, temperatura y humedad en ese orden.
def get_DHT():
    try:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        humidity=round(humidity,2)
        temperature=round(temperature,2)
        return True, humidity, temperature
    except:
        return False, 0, 0


# Inicializa y delcara los eventos de interrupcion de hardware tras cambio de estado de una terminal GPIO (btn)
# pressed y released son funciones declaradas previamente en el documento. 
def Hardware_Interruption_init():
    if btn.is_pressed:                  
        os.environ["Power"]='ENCENDIDO' # variable de hambiente, delcara el estado del pin GPIO a todo el hambiente de trabajo 
    else:
        os.environ["Power"]='APAGADO'
    btn.when_pressed = pressed
    btn.when_released = released

if __name__ == '__main__':
    DHT_Flag, hum, temp=get_DHT()
    print(DHT_Flag)
    print(temp)
    print(hum)