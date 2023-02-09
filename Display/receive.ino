#include <EthernetENC.h>
#include <SPI.h>
#include <PubSubClient.h>


int count = 0;
String transmit;
char b[8];

const char* mqtt_server = "192.168.1.165";
const int mqtt_port = 1883;
const char* mqttUser = "getparking";
const char* mqttPassword = "playtmbiz";

EthernetClient ethClient;
PubSubClient client(ethClient);

IPAddress ip(192,168,1,225);
IPAddress gwip(192,168,1,1);
IPAddress subnet (255,255,255,0);

byte mac[] = {  0x14, 0xED, 0xBA, 0xFE, 0xFE, 0x00 };
unsigned long lastMsg = 0;
const char* post = "P2/";
const char*  fetch = "dmd/";


void callback(char* topic, byte* message, unsigned int length);
void callback(char* topic, byte* payload, unsigned int length)
{
  //publishMessage(fetch, "message aaya", true);
  // Serial.print("Message arrived [");
  // Serial.print(topic);
  // Serial.print("] ");\
  
  String str;
  for (int i = 0; i < length; i++)
  {
    // Serial.write((char)payload[i]);
    str += (char)payload[i];
    //Serial.print(str);
  }
  transmit = str;
  Serial.print(transmit);
  // int str_len = str.length() + 1;
  // char char_array[str_len];
  // str.toCharArray(char_array, str_len);
  // Serial.print(char_array);
  //Serial.write(char_array,3);
  publishMessage(fetch, str, true);
  //Serial.println();
}
void setup()
{

  Serial.begin(9600);
  while (!Serial) delay(1);
  Ethernet.begin(mac,ip,gwip,subnet);
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  //Serial.print(transmit);
}

void reconnect()
{
  if (client.connect("arduinoClientSuper214", mqttUser, mqttPassword))
  {
    Serial.println("041");
    client.subscribe(post);
    publishMessage(fetch, "P2 display connected", true);
  }
  else
  {
    // Serial.print("failed, rc=");
    // Serial.print(client.state());
    // Serial.println(" try again in 5 seconds");
    delay(1000);
  }
}
void loop()
{
  Ethernet.maintain();
  while (!client.connected())
  {
    //Serial.println("Connecting to MQTT...");
    reconnect();
  }
  client.loop();
}

void publishMessage(const char* topic, String payload , boolean retained)
{
  if (client.publish(topic, payload.c_str(), true))
    int Var= 15;
  //Serial.println("Message publised [" + String(topic) + "]: " + payload);
}
