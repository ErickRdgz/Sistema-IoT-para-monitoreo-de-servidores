import os
from typing import cast


## Secuencias binarias basicas para la codificacion de comandos a su equivalente en binario.  
ONES='1111'
ZEROS='0000'
BASE_CODE='1011001001001101'
TEMP_CODES= [['0000' ,'0001',	'0011','0010',	'0110',	'0111',	'0101',	'0100',	'1100',	'1101',	'1001',	'1000',	'1010',	'1011'],['1111','1110','1100','1101','1001','0111','1010','1011','0011','0010','0110','0111','0101','0100']]
FAN_CODES=[['1011','1001','0101','0011'],['0100','0110','1010','1100']]
MODE_CODES= [['1000','0100','0000','1100 '],['0111','1011','1111','0011']]

MIN_TEMP=17
MAX_TEMP=30


#Esta funcion recibe la codificacion binaria construida por Send_Command y a partir de este construlle la secuencia de codificacion en tiempos del comando, 
# la interpretacion de cada digito binario o "separador" se construlle a partir de la conjuncion de dos lapsos de tiempo ( uno de encendido y y uno de apagado)
# 
def Create_Signal(CODE):
    BASE =  '520'
    SHORT=  '550'
    LONG = '1640'

    SEPARATOR1='4400'
    SEPARATOR2='5300'
    SIGNAL=''

    for x in CODE:   # el ciclo recorrera el codigo binario bit a bit para ir construyendo la secuencia de tiempos
        if(x=='0'):
            SIGNALA= ' '+ BASE + ' '+ SHORT
        elif(x=='1'):
            SIGNALA= ' '+ BASE + ' '+ LONG
        elif(x=='['):
            SIGNALA= ' '+ SEPARATOR1 + ' '+ SEPARATOR1
        elif(x==']'):
            SIGNALA= ' '+ BASE + ' '+ SEPARATOR2
        SIGNAL=SIGNAL +SIGNALA
    return SIGNAL



#  a partir de la codificacion en tiempos de la instruccion se escribe un documento de extension 
#  .lircd.conf que es el formato requerido por el software LIRC para ejecutar el comando.
#  las lienas dicionales agregadas al archivo son  prametros de incializacion y configuracion de LIRC
def Write_File(CODE):
    # print (CODE)
    file = open("Ctrl.lircd.conf", "w")
    file.write("begin remote \n  \n name  Ctrl \n eps            30 \n aeps          100\n \n gap          34978 \n \n      begin raw_codes \n \n    name COMMAND \n \n")
    file.write(CODE)
    file.write(" 527 ")
    file.write("\n \n   end raw_codes \n end remote")
    file.close()



# Recibe la codificacion binaria y gestiona los pasos para la ejecucion de la instruccion.
def Execute_Command(SIGNAL_CODE):
    # print(SIGNAL_CODE)
    SIGNAL=Create_Signal(SIGNAL_CODE)  # crea la codificacion de triempos a partir de la codificacion binaria
    Write_File(SIGNAL)      # crea  el achivo de parametros para ejecutar el comando en LIRC
    try:                    # lirc se ejecuta desde terminal del sistema, a partir de la libreria .os se accedio a termnal
        os.system("sudo /etc/init.d/lircd stop")            # se detiene el servicio de LIRC
        os.system("sudo cp /home/pi/workSpace/Ctrl.lircd.conf /etc/lirc/lircd.conf.d/")     # copia el archivo "Ctrl" con el comando  al directorio de LIRC
        os.system("sudo /etc/init.d/lircd start")           # inicia el servicio de LIRC
        os.system("irsend SEND_ONCE Ctrl COMMAND")          # ejecuta el comando COMMAND del archivo Ctrl
        return True
    except:
        return False


#Esta funcion codifica el comando a enviarse al equipo de climatizacion para posteriormente ser preparado y enviado a su ejecucion.  de no recibir parametros se ejecutara con los valores por defecto establecidos
# la codificacion del comando en binario dependerá del equipo de climatizacion en cuestion, los metodos de condificacion empleados en esta funcion se describen a mayor profuncidad en la documentacion.


def Send_Command(Mode='COLD',Temperature=21,fan_Speed=0,Sleep='OFF', POWER='ON'):
    # print("Testeando ejecucion Encode_Signal")
    CODE=''
    SIGNAL_CODE=''  
    if POWER=='ON':
        if Mode=='COLD':
            CODE= BASE_CODE + FAN_CODES[0][fan_Speed] + ONES + FAN_CODES[1][fan_Speed] + ZEROS + TEMP_CODES[0][Temperature-MIN_TEMP] + MODE_CODES[0][2]+ TEMP_CODES[1][Temperature-MIN_TEMP] + MODE_CODES[1][2]
            SIGNAL_CODE='['+ CODE+']['+ CODE
            if Sleep =='ON':
                SIGNAL_CODE='[101100100100110111100000000111110000001111111100]'+ SIGNAL_CODE
            if Execute_Command(SIGNAL_CODE):
                return True
            else:
                return False

        elif Mode=='AUTO':
            CODE= BASE_CODE + FAN_CODES[0][fan_Speed] + ONES + FAN_CODES[1][fan_Speed] + ZEROS + TEMP_CODES[0][Temperature-MIN_TEMP] + MODE_CODES[0][0]+ TEMP_CODES[1][Temperature-MIN_TEMP] + MODE_CODES[1][0]
            SIGNAL_CODE='['+ CODE+']['+ CODE
            if Sleep =='ON':
                SIGNAL_CODE='[101100100100110111100000000111110000001111111100]'+ SIGNAL_CODE
            if Execute_Command(SIGNAL_CODE):
                return True
            else:
                return False

        elif Mode=='DRY':
            CODE= BASE_CODE + FAN_CODES[0][fan_Speed] + ONES + FAN_CODES[1][fan_Speed] + ZEROS + TEMP_CODES[0][Temperature-MIN_TEMP] + MODE_CODES[0][1]+ TEMP_CODES[1][Temperature-MIN_TEMP] + MODE_CODES[1][1]
            SIGNAL_CODE='['+ CODE+']['+ CODE
            if Sleep =='ON':
                SIGNAL_CODE='[101100100100110111100000000111110000001111111100]'+ SIGNAL_CODE
            if Execute_Command(SIGNAL_CODE):
                return True
            else:
                return False

        elif Mode=='HEAT':
            CODE= BASE_CODE + FAN_CODES[0][fan_Speed] + ONES + FAN_CODES[1][fan_Speed] + ZEROS + TEMP_CODES[0][Temperature-MIN_TEMP] + MODE_CODES[0][3]+ TEMP_CODES[1][Temperature-MIN_TEMP] + MODE_CODES[1][3]
            SIGNAL_CODE='['+ CODE+']['+ CODE
            if Sleep =='ON':
                SIGNAL_CODE='[101100100100110111100000000111110000001111111100]'+ SIGNAL_CODE
            if Execute_Command(SIGNAL_CODE):
                return True
            else:
                return False

        elif Mode=='SWING':
            SIGNAL_CODE='[101100100100110101101011100101001110000000011111][101100100100110101101011100101001110000000011111'
            if Execute_Command(SIGNAL_CODE):
                return True
            else:
                return False

        else:
            return False

             
    elif POWER=='OFF':
        SIGNAL_CODE='[101100100100110101111011100001001110000000011111][101100100100110101111011100001001110000000011111'
        if Execute_Command(SIGNAL_CODE):
            return True
        else:
            return False

    else:
        return False


 
if __name__ == '__main__':
    Send_Command()


