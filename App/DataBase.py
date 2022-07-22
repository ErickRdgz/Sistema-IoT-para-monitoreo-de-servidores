from mysql.connector import (connection)
from mysql.connector import errorcode


def SaveData(Temp, Hum):
    try:
        cnx = connection.MySQLConnection(user='sensor', password='ABC%123#abc', host='192.168.18.180', database='sensores')
        cursor = cnx.cursor()
        print('Datos Salvados')
        add_data=("INSERT INTO Sensor(Temperatura, Humedad, fecha) VALUES (%s,%s, CURRENT_TIMESTAMP)")
        data=(Temp,Hum) 
        cursor.execute(add_data, data)
        cnx.commit()
        cursor.close()
        cnx.close()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cnx.close()




def SaveData_MQTT(Temp, Hum):
    try:
        cnx = connection.MySQLConnection(user='sensor', password='ABC%123#abc', host='192.168.18.180', database='sensores')
        cursor = cnx.cursor()
        print('Datos MQTT salvados')
        add_data=("INSERT INTO Sensor_MQTT(Temperatura, Humedad, fecha) VALUES (%s,%s, CURRENT_TIMESTAMP)")
        data=(Temp,Hum) 
        cursor.execute(add_data, data)
        cnx.commit()
        cursor.close()
        cnx.close()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cnx.close()
    

if __name__ == '__main__':
    SaveData_MQTT('hhh', 'tttt')
