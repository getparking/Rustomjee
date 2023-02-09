#include <EthernetENC.h>
#include <PubSubClient.h>
#include <SPI.h>

const int trigPin = 9;
const int echoPin = 8;
int previous = 0;
int sensorValue = 3;
int voltage;
int count = 0;
long duration;
int distance;
String dist;

const char* mqtt_server = "192.168.1.165"; 
const int mqtt_port = 1883; 
const char* mqttUser = "getparking";
const char* mqttPassword = "playtmbiz";

EthernetClient ethClient;
PubSubClient client(ethClient);

IPAddress ip(192,168,1,222);
IPAddress gwip(192,168,1,1);
IPAddress subnet (255,255,255,0);

byte mac[] = {0x22, 0xED, 0xBA, 0xFE, 0xFE, 0x00 };

unsigned long lastMsg = 0;
const char*pub = "loop/"; 
const char* sub = "data_T/";

String Car;
String stri;

void callback(char* topic, byte* message, unsigned int length);
void callback(char* topic, byte* payload, unsigned int length)
{
 for (int i = 0; i < length; i++)
  {
    Serial.print((char)payload[i]);
    Car += (char)payload[i];
  }
}

void setup()
{
  Serial.begin(9600);
  while (!Serial) delay(1);
  Ethernet.begin(mac,ip,gwip,subnet);
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  pinMode(sensorValue, INPUT_PULLUP);
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input
}
void reconnect()
{
  if (client.connect("arduinoClientSup222", mqttUser, mqttPassword))
  {
    publishMessage(sub,"Connected loop test", true);
    client.subscribe(sub);
  }
  else
  {
    Serial.print("failed, rc=");
    Serial.print(client.state());
    delay(100);
  }
}

void publishMessage(const char* topic, String payload , boolean retained)
{
  if (client.publish(topic, payload.c_str(), true))
    Serial.println("Message publised [" + String(topic) + "]: " + payload);
}
void loop()
{
  Ethernet.maintain();
  while (!client.connected())
  {
    Serial.println("Connecting to MQTT...");
    reconnect();
  }
  client.loop();
  ultrasonic();
  if(distance <= 200 ){
    voltage = digitalRead(sensorValue);
    if ( voltage != LOW)
    {
      Serial.println("voltage is :");
      Serial.println(voltage);
    }
    else
    {
      Serial.print("Car hai");
      Serial.println(voltage); 
      if (previous == LOW)
      {
        Serial.println("Same car");
      }
      else
      {
        count ++;
        String vehicle = String(count);
        Serial.print("count is ");
        Serial.println(count);
        publishMessage(pub,"en1", true);
       // publishMessage(pub,dist, true);
      }
    }
    previous = voltage;
   }
  else
  {
    Serial.println("No Car");
    
  }
}

void ultrasonic (){
   digitalWrite(trigPin, LOW);
  digitalWrite(trigPin, HIGH);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034 / 2;
  dist = String(distance);
}
