from importlib import import_module
import os
from flask import Flask, render_template, Response,stream_with_context
import schedule #import every, repeat, run_pending
import time
import threading
from threading import Lock
import eventlet
import json
from flask_socketio import SocketIO
from flask_mqtt import Mqtt
import logging


import DataBase as DB

# MODULOS DE CONTROL DE HARDWARE.............
from camera_pi import Camera
import AC_Encoder as AC_Controler
import Hardware  

# MODULOS DE SIMULACION.............
# from camera import Camera
# import AC_Encoder_Sim as AC_Controler
# import Hardware_Sim as Hardware 


# eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET'] = 'my secret key'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = 'localhost'
app.config['MQTT_BROKER_PORT'] = 1883
# app.config['MQTT_CLIENT_ID'] = 'flask_mqtt'
app.config['MQTT_CLEAN_SESSION'] = True
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False
# app.config['MQTT_LAST_WILL_TOPIC'] = 'home/lastwill'
# app.config['MQTT_LAST_WILL_MESSAGE'] = 'bye'
app.config['MQTT_LAST_WILL_QOS'] = 2

# Parameters for SSL enabled
# app.config['MQTT_BROKER_PORT'] = 8883
# app.config['MQTT_TLS_ENABLED'] = True
# app.config['MQTT_TLS_INSECURE'] = True
# app.config['MQTT_TLS_CA_CERTS'] = 'ca.crt'

socketio = SocketIO(app)
mqtt = Mqtt(app)
streaming_thread=None
streaming_flag=False
thread_lock = Lock()
client_conter=0

MQTT_flag=False
SaveData_flag=False
MQTT_Temperature=0
MQTT_Humidity=0


# Funcion decoradora para la ejecucion de Shedule en segundo plano
# implementacion propuesta en la documentacion de Schedule
def run_continuously(interval=1):
    cease_continuous_run = threading.Event()
    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)
    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


# Esta funcion se encargara de salvar la temperatura y humedad en la base de datos
# se ejecuta en un hilo en segundo plano 
def background_job():
    mqtt.publish('Ctrl/ESP2', 'GET' )
    global SaveData_flag
    SaveData_flag=True
    DHT_Flag, humidity, temperature =Hardware.get_DHT()   
    if DHT_Flag:
        DB.SaveData(str(temperature),str(humidity))
    else:
        print('Error de lectura')

    

# Ejecuta  background_job cada 60 segundos, usado para pruebas 
schedule.every(60).seconds.do(background_job)
# Run job every hour at the 30rd minute
#schedule.every().hour.at(":30").do(background_job)
    

# El hilo se inicializa cuando hay algun cliente SocketIO y se detendra si no hay clientes
# su objetivo es  Streaming de datos (Temperatura y humedad ), supervicion del estado del sensor de corriente electrica 
# a partir de la varible de estado asignada  y solicitud de temperatura al dispositivo MQTT 
def background_streaming_thread():
    contador_strimeado=0
    while True:
        global streaming_flag   # esta varibale estará en alto siempre que haya al menos un cliente.
        if streaming_flag:    
            Alerta=os.getenv('Power')   # lectura de variable de estado
            if Alerta=='APAGADO':
                socketio.emit('Power', False)
            else:
                socketio.emit('Power', True)

            mqtt.publish('Ctrl/ESP2', 'GET' )    #Solicitud MQTT de temperatura al modulo Wifi 
            DHT_Flag, humidity, temperature =Hardware.get_DHT()
            if DHT_Flag:
                Stream_data = dict(
                    Temperature=temperature,
                    Humidity=humidity,
                )
                socketio.emit('Stream_Data', Stream_data) # emision por socket de datos a la pagina web
            else:
                print('Error de lectura para Streaming')

            socketio.sleep(10)
        else:
            MQTT_flag=False
            break


#el Streaming de video esta basado en una funcion  generativa  de flask,  la funcion generativa obtendrá 
# el video frame a frame del modulo camara.
def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# la ruta devolvera una pagina html con Streaming de video
@app.route('/Camera')
def index_video():
    """Video streaming home page."""
    return render_template('index_video.html')


# la ruta devuelve unicamnete el Streaming de video, la pagina de la ruta "/Camera" recibira de esta ruta la imagen frame a frame
# ejecuta una funcion generativa para obtener los frames
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


# recibe informacion por un cliente de la pagina web a traves de un  evento de socket.
# ejecuta una orden al equipo de climatizacion a traves del modulo AC_Controler
@socketio.on('AC_OFF')
def handle_AC_OFF(msg):
    if AC_Controler.Send_Command(POWER='OFF'):
        socketio.emit('Server_Response', 'Aire Acondicionado Apagado')
        print('Aire Acondicionado Apagado')
    else:
        socketio.emit('Server_Response', 'Error al Enviar Orden')
        print('Error al Enviar Orden')

# ejecuta una orden de configuracion de parametros al equipo de climatizacion 
@socketio.on('AC_Control')
def handle_AC_Control(data_Json):
    data = json.loads(data_Json)
    if AC_Controler.Send_Command(Mode='COLD',Temperature=data['Temperature'],fan_Speed=0,Sleep=data['Sleep'], POWER='ON'):
        socketio.emit('Server_Response', 'Aire acondicionado Listo!!')
        print('Aire acondicionado Listo!!')
    else:
        socketio.emit('Server_Response', 'Error al Enviar Orden')
        print('Error al Enviar Orden')


# evento disparado con cada acceso de clientes a la pagina web, de ser el primer cliente inicialzara 
# un thread para Streaming de datos. 
@socketio.on('connect')
def test_connect():
    global client_conter
    client_conter +=1
    print("Cliente conectado, Numero de clientes: ", client_conter)
    global streaming_thread
    global streaming_flag
    streaming_flag=True
    with thread_lock:
        if streaming_thread is None:
            streaming_thread = socketio.start_background_task(background_streaming_thread)


# con cada salida de clientes se ejecutará, de no habier cleintes detendra el thread de Streaming 
@socketio.on('disconnect')
def test_disconnect():
    global client_conter
    global streaming_thread
    global streaming_flag
    client_conter -=1
    print("Cliente desconectado, Numero de clientes: ", client_conter)
    if  client_conter<1:
        streaming_flag=False
        streaming_thread=None


# evento a espera de mensajes MQTT de los topics a los que se está subscrito 
# para el caso particular del sistema recibirá la temperatura del modulo wifi 
#guardara la informacion en la bse da datos o la publicara en la pagina segun sea el caso.
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    msg=message.payload.decode()   

    if message.topic == 'Temperature/ESP2':
        data=json.loads(message.payload.decode())
        MQTT_Temperature=data['Temperature']
        MQTT_Humidity=data['Humidity']
        global streaming_flag
        global SaveData_flag
        if streaming_flag==True:
            Stream_Data= dict(
                Temperature=MQTT_Temperature,
                Humidity=MQTT_Humidity,
            )
            socketio.emit('Stream_Data_MQTT',Stream_Data)
        if SaveData_flag:
            DB.SaveData_MQTT(MQTT_Temperature,MQTT_Humidity)
            SaveData_flag=False



if __name__ == '__main__':
    Hardware.Hardware_Interruption_init()   # inicializacion de la interrupcion de hardware para supervicion de corriente electrica
    stop_run_continuously = run_continuously() # inicializa  el hilo de recoleccion de datos
    mqtt.subscribe('Temperature/#')         # subscripcion al topic de temperatura. 

    socketio.run(app, host='0.0.0.0',port=5000,use_reloader=False,debug=True)  # arranque del sistema 