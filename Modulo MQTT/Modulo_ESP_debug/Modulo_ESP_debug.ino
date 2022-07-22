#include <WiFiManager.h> 
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "FS.h"
#include <LittleFS.h>

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE  (50)
char msg[MSG_BUFFER_SIZE];
int value = 0;
String MQTTmsg="";


WiFiManager wm; // global wm instance
WiFiManagerParameter custom_field; // global param ( for non blocking w params )
bool shouldSaveConfig = false; //flag for saving data




  const char* ESPname         ="ESP2";
  const char* ESPpassword     ="12345678";
  const char* MQTT_server     ="11111111111";
  const char* MQTTuser        ="111111111";
  const char* MQTTpassword    ="1111111111";
  const char* MQTTport        ="1883";
  const char* CtrlTopic       ="1111111";
  const char* StatusTopic   =  "11111";
  const char* TempTopic      = "1111111";

  String ESPname_s         ="";
  String ESPpassword_s     ="";
  String MQTT_server_s     ="";
  String MQTTuser_s        ="";
  String MQTTpassword_s    ="";
  int MQTTport_s           =0;
  String CtrlTopic_s       ="";
  String StatusTopic_s     ="";
  String TempTopic_s       ="";


 
#define LED 3
#define BUTTON 0
int buttonState = 0; 


void saveConfigCallback () {
  Serial.println("Should save config");
  shouldSaveConfig = true;
}


//MQTT data reception
void callback(char* topic, byte* payload, unsigned int length) {
  // digitalWrite(LED,HIGH);
  // delay(50);
  // digitalWrite(LED,LOW);
  // delay(50);
  // digitalWrite(LED,HIGH);
  // delay(50);
  // digitalWrite(LED,LOW);

     Serial.print("Message arrived [");
     Serial.print(topic);
     Serial.print("] ");
  MQTTmsg="";
  for (int i = 0; i < length; i++) {
    MQTTmsg+=(char)payload[i];
  } 
  // if(topic=="CTRL/ESP2"){
  if(MQTTmsg=="GET"){
    client.publish(TempTopic_s.c_str(),"tep");
  }
  // }
}



 //reconnection with MQTT server
void reconnect() {
  
  while (!client.connected()) {     // Loop until we're reconnected
     Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.publish(StatusTopic_s.c_str(), "ON-LINE");
      client.subscribe(CtrlTopic_s.c_str());
    } else {
       Serial.print("failed, rc=");
      Serial.print(client.state());
       Serial.println(" try again in 5 seconds");
      // digitalWrite(LED,HIGH);
      // delay(300);
      // digitalWrite(LED,LOW);
      // delay(300);
      // digitalWrite(LED,HIGH);
      // delay(300);
      // digitalWrite(LED,LOW);
      // delay(300);
      // digitalWrite(LED,HIGH);
      // delay(300);
      // digitalWrite(LED,LOW);
       delay(1000);
      
    }
  }
}






void setup() {
  
  WiFi.mode(WIFI_STA); // explicitly set mode, esp defaults to STA+AP  
  Serial.begin(115200);
  Serial.setDebugOutput(true); 
  // pinMode(BUTTON, INPUT);
  // pinMode(LED,OUTPUT);

  // digitalWrite(LED,HIGH);
  // delay(500);
  // digitalWrite(LED,LOW);
  // delay(500);
  // digitalWrite(LED,HIGH);
  // delay(500);
  // digitalWrite(LED,LOW);
  // delay(500);
  // digitalWrite(LED,HIGH);
  // delay(500);
  // digitalWrite(LED,LOW);
  delay(5000);
  
  

    Serial.println("mounting FS...");


  // Read data from SPIFFS
  if (SPIFFS.begin()) {
    Serial.println("mounted file system");
    if (SPIFFS.exists("/config.json")) {     //file exists, reading and loading    
      Serial.println("reading config file");
      File configFile = SPIFFS.open("/config.json", "r");
      if (configFile) {
        Serial.println("opened config file");
        size_t size = configFile.size();   
        std::unique_ptr<char[]> buf(new char[size]);   // Allocate a buffer to store contents of the file.
        configFile.readBytes(buf.get(), size);
        Serial.println(buf.get());
        
        StaticJsonDocument<900> doc;
        DeserializationError error = deserializeJson(doc, buf.get());
        if (error) {
          Serial.println("Failed to parse config file");
          // Execution_error();     
        }else{

          ESPname = doc["ESPname"];
          ESPpassword = doc["ESPpassword"];
          MQTT_server = doc["MQTTserver"];   
          MQTTuser = doc["MQTTuser"];
          MQTTpassword = doc["MQTTpassword"];
          MQTTport = doc["MQTTport"];
          CtrlTopic = doc["CtrlTopic"];
          StatusTopic = doc["StatusTopic"];
          TempTopic = doc["Temperature"];

          ESPname_s=String(ESPname);
          ESPpassword_s=String(ESPpassword);
          Serial.println(ESPname_s);
          Serial.println(ESPpassword_s);

          // strcpy(ESPname, doc["ESPname"]);
          // // strcpy(ESPpassword, doc["ESPpassword"]);
          // strcpy(MQTT_server, doc["MQTTserver"]);
          // // strcpy(MQTTuser, doc["MQTTuser"]);
          // // strcpy(MQTTpassword, doc["MQTTpassword"]);
          // // strcpy(MQTTport, doc["MQTTport"]);
          // // strcpy(CtrlTopic, doc["CtrlTopic"]);
          // StatusTopic= (doc["StatusTopic"]);
          // // auto StatusTopic = doc["StatusTopic"].as<String>();
          // // strcpy(StatusTopic, doc["StatusTopic"]);
          // // strcpy(TempTopic, doc["TempTopic"]);

          // Serial.println(MQTT_server);
          // Serial.println(StatusTopic);
        }
      }
    }
  }else {
    Serial.println("failed to mount FS");
    // Execution_error();
  }
  // The extra parameters to be configured (can be either global or just in the setup)
  // After connecting, parameter.getValue() will get you the configured value
  // id/name placeholder/prompt default length
  WiFiManagerParameter custom_ESPname("ESP name", "ESP name", ESPname, 30);
  WiFiManagerParameter custom_ESPpassword("ESP password", "ESP password", ESPpassword, 32);
  WiFiManagerParameter custom_mqtt_server("MQTT server", "MQTT server", MQTT_server, 20);
  WiFiManagerParameter custom_mqtt_user("MQTT user", "MQTT user", MQTTuser, 30);
  WiFiManagerParameter custom_mqtt_password("MQTT password", "MQTT password", MQTTpassword, 32);
  WiFiManagerParameter custom_mqtt_port("MQTT port", "MQTT port", MQTTport, 6);
  WiFiManagerParameter custom_mqtt_Ctrl("Ctrl Topic", "Ctrl Topic", CtrlTopic, 20);
   WiFiManagerParameter custom_mqtt_Status("Status Topic", "Status Topic", StatusTopic, 20);
  WiFiManagerParameter custom_mqtt_Temp("Temp Topic", "Temp Topic", TempTopic, 20);

    //set config save notify callback
  wm.setSaveConfigCallback(saveConfigCallback);
  wm.addParameter(&custom_ESPname);
  wm.addParameter(&custom_ESPpassword);
  wm.addParameter(&custom_mqtt_server);
  wm.addParameter(&custom_mqtt_user);
  wm.addParameter(&custom_mqtt_password);
  wm.addParameter(&custom_mqtt_port);
  wm.addParameter(&custom_mqtt_Ctrl);
  wm.addParameter(&custom_mqtt_Status);
  wm.addParameter(&custom_mqtt_Temp);


  //  Serial.begin(115200);
  //  Serial.setDebugOutput(true);   
  //  delay(5000);
  //  Serial.println("\n Starting");
  
  
  
  int customFieldLength = 40;   // add a custom input field
  const char* custom_radio_str = "<br/><label for='customfieldid1'>Configuracion</label><br><br>Name <br><input type='text' name='NameField' value='ESP2'> Password Server<br><input type='text' name='PwField' value='12345678'> MQTT Server<br><input type='text' name='ServerField' value='192.168.1.69'>MQTT User<br><input type='text' name='MQTTUrField' value='ESP2'>MQTT Password<br><input type='text' name='MQTTPWField' value='12345678'>MQTT Port<br><input type='text' name='MQTTPortFd' value='1883'>Control Topic<br><input type='text' name='ControlField' value='Ctrl/ESP2'>Status Topic<br><input type='text' name='StatusField' value='Status/ESP2'>Temperature Topic<br><input type='text' name='TempField' value='Temperature/ESP2'><br>";
  new (&custom_field) WiFiManagerParameter(custom_radio_str); // custom html input

   //wm.resetSettings(); // wipe settings
  //wm.setDebugOutput(false);   // disable Debug
  wm.addParameter(&custom_field); 
  wm.setSaveParamsCallback(saveParamCallback);
  wm.setAPCallback(configModeCallback);
  Serial.println("ddddddddddddddddddddddddddd");
  // custom menu via array or vector
  // menu tokens, "wifi","wifinoscan","info","param","close","sep","erase","restart","exit" (sep is seperator) (if param is in menu, params will not show up in wifi page!)
  std::vector<const char *> menu = {"wifi","info","param","sep","restart","exit"};
  wm.setMenu(menu);
  
  wm.setClass("invert"); // set dark theme
  wm.setConfigPortalTimeout(80); // auto close configportal after n seconds
  Serial.println("ddddddddddddddddddddddddddd");
  bool res;
  res = wm.autoConnect(ESPname_s.c_str(),ESPpassword_s.c_str()); // password protected ap
  Serial.println("ddddddddddddddddddddddddddd");
  if(!res) {
   Serial.println("Failed to connect or hit timeout");
    // ESP.restart();
    // digitalWrite(LED,HIGH);
    // delay(200);
    // checkButton();
    // digitalWrite(LED,LOW);
    // delay(200);
  } 
  else {
    //if you get here you have connected to the WiFi    
   Serial.println("connected...yeey :)");
    // digitalWrite(LED,HIGH);
    // delay(2000);
    // digitalWrite(LED,LOW);
    // delay(100);
    // digitalWrite(LED,HIGH);
    // delay(200);
    // digitalWrite(LED,LOW);
    // delay(100);
    // digitalWrite(LED,HIGH);
    // delay(200);
    // digitalWrite(LED,LOW);
  }
  
  ESPname= custom_ESPname.getValue();
  ESPpassword= custom_ESPpassword.getValue();
  MQTT_server= custom_mqtt_server.getValue();
  MQTTuser= custom_mqtt_user.getValue();
  MQTTpassword= custom_mqtt_password.getValue();
  MQTTport= custom_mqtt_port.getValue();
  CtrlTopic= custom_mqtt_Ctrl.getValue();
  StatusTopic= custom_mqtt_Status.getValue();
  TempTopic= custom_mqtt_Temp.getValue();

 ESPname_s=String(ESPname);
 ESPpassword_s=String(ESPpassword);
 MQTT_server_s=String(MQTT_server);
 MQTTuser_s=String(MQTTuser);
 MQTTpassword_s=String(MQTTpassword);
 MQTTport_s= atoi(MQTTport);
 CtrlTopic_s= String(CtrlTopic);
 StatusTopic_s=String(StatusTopic);
 TempTopic_s=String(TempTopic);

  Serial.println(MQTT_server);  
  Serial.println(MQTTport_s);
  Serial.println(TempTopic);

  client.setServer(MQTT_server_s.c_str(), MQTTport_s);
  client.setCallback(callback);

  // digitalWrite(LED, LOW);


}




 // check for button press, the button initializes the configuration server

void checkButton(){
  if ( true) {  // poor mans debounce/press-hold, code not ideal for production
    delay(2000);
    if( true){

      client.publish(StatusTopic_s.c_str(), "INICIANDO CONFIGURACION...");
      wm.setConfigPortalTimeout(300);
      
      if (!wm.startConfigPortal(ESPname,"12345678")) {
        Execution_error();
      } 
    }
  }
}


void Execution_error(){
  // int counter=0; 
  //       while (counter<=400){
  //         digitalWrite(LED,HIGH);
  //         delay(500);
  //         digitalWrite(LED,LOW);
  //         delay(500);
  //         digitalWrite(LED,HIGH);
  //         delay(500);
  //         digitalWrite(LED,LOW);
  //         delay(500);
  //         digitalWrite(LED,HIGH);
  //         delay(500);
  //         digitalWrite(LED,LOW);
  //         delay(500);
  //         counter++;
  //       }
  //       ESP.restart();
}

String getParam(String name){
  //read parameter from server, for customhmtl input
  String value;
  if(wm.server->hasArg(name)) {
    value = wm.server->arg(name);
  }
  return value;
}

void saveParamCallback(){

    StaticJsonDocument<900> doc;
  doc["ESPname"]=getParam("NameField");
  doc["ESPpassword"]=getParam("PwField");
  doc["MQTTserver"]=getParam("ServerField");
  doc["MQTTuser"]=getParam("MQTTUrField");
  doc["MQTTpassword"]=getParam("MQTTPWField");
  doc["MQTTport"]=getParam("MQTTPortFd");
  doc["CtrlTopic"]=getParam("ControlField");
  doc["StatusTopic"]=getParam("StatusField");
  doc["Temperature"]=getParam("TempField");

  
  Serial.println(getParam("NameField"));




  File configFile = SPIFFS.open("/config.json", "w");
  if (configFile) {
       serializeJson(doc, configFile);
  } else{
     Serial.println("ERORRRRRRRRRRR");
  }



//   // Serial.println("[CALLBACK] saveParamCallback fired");
//   MQTTdata2.MQTTIP=getParam("IPField");
//   MQTTdata2.CtrlTopic=getParam("ControlField");
//   MQTTdata2.StatusTopic=getParam("StatusField");
//   MQTTdata2.TempTopic=getParam("TemperatureField");
  
// //  Serial.println("PARAM customfieldid = " + MQTTdata2.MQTTIP );
// //  Serial.println("PARAM customfieldid = " + MQTTdata2.CtrlTopic);
// //  Serial.println("PARAM customfieldid = " + MQTTdata2.StatusTopic);
// //  Serial.println("PARAM customfieldid = " + MQTTdata2.TempTopic);

//   EEPROM.put(0, MQTTdata2);
//   boolean ok = EEPROM.commit();
  
//   //Serial.println((ok) ? "Commit OK" : "Commit failed");


//   EEPROM.get(0, MQTTdata2);
//  // Serial.println("PARAM customfieldidddddd = " + MQTTdata2.CtrlTopic);
}



void configModeCallback (WiFiManager *myWiFiManager) {
  // digitalWrite(LED, HIGH);
  // delay(50);
  // digitalWrite(LED, LOW);
  // delay(50);
  // digitalWrite(LED, HIGH);
  // delay(50);
  // digitalWrite(LED, LOW);
  // delay(50);
  // digitalWrite(LED, HIGH);
  // delay(50);
  // digitalWrite(LED, LOW);
  // delay(50);
  // digitalWrite(LED, HIGH);
  // delay(50);
  // digitalWrite(LED, LOW);
  // delay(50);
  // digitalWrite(LED, HIGH);
  // delay(50);
  // digitalWrite(LED, LOW);
  
}




void loop() {

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > 2000) {
    lastMsg = now;
    ++value;
    snprintf (msg, MSG_BUFFER_SIZE, "hello world #%ld", value);
    client.publish(TempTopic_s.c_str(), msg);
  }

  //checkButton();
}
