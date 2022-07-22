import random

def get_DHT():
    
    humidity= random.randint(50,100)
    temperature = random.randint(20,30)
    return True, humidity, temperature
   

def Hardware_Interruption_init():
    print('Iniciando interrupciones de Hardware....')

if __name__ == '__main__':
    DHT_Flag, hum, temp=get_DHT()
    print(DHT_Flag)
    print(temp)
    print(hum)