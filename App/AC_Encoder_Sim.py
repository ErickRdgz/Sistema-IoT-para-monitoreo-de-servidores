

def Send_Command(Mode='COLD',Temperature=19,fan_Speed=0,Sleep='OFF', POWER='ON'):#SETTINGS ): 
    print('Enviando señal IR.....')
    print('Mode',Mode,' Temperature:',Temperature,'  Sleep:',Sleep)
    return True
 
if __name__ == '__main__':
    #Encode(Mode='COLD',Temperature=19,fan_Speed=0,Sleep='OFF', POWER='ON')
    Send_Command()

    #Execute_Command(CODE)

