#include <EthernetENC.h>
#include <SPI.h>
#include <PubSubClient.h>

int count = 0;
String transmit;
char b[8];

const char* mqtt_server = "192.168.1.211";
const int mqtt_port = 1883;
const char* mqttUser = "getparking";
const char* mqttPassword = "playtmbiz";

EthernetClient ethClient;
PubSubClient client(ethClient);

long lastReconnectAttempt = 0;

IPAddress ip(192, 168, 1, 99);
IPAddress gwip(192, 168, 1, 1);
IPAddress subnet (255, 255, 255, 0);

byte mac[] = { 0x14, 0xED, 0xBA, 0xFE, 0xFE, 0x00 };
unsigned long lastMsg = 0;
const char* sub = "P2/";
const char* post = "dmd_P2/";

void callback(char* topic, byte* message, unsigned int length);
void callback(char* topic, byte* payload, unsigned int length)
{
  String str;
  for (int i = 0; i < length; i++)
  {
    str += (char)payload[i];
  }
  transmit = str;
  Serial.print(transmit);
  publishMessage(post, str, true);
 
}

void setup()
{
  Serial.begin(9600);
  while (!Serial) delay(1);
  Ethernet.begin(mac, ip, gwip, subnet);
 // Ethernet.begin(mac);
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  client.setKeepAlive(60);
  delay(1500);
  long lastReconnectAttempt = 0;
}

boolean reconnect() {
  if (client.connect("arduinoClient",mqttUser, mqttPassword)) {
    // Once connected, publish an announcement...
    publishMessage(post,"Connected",true);
    // ... and resubscribe
    client.subscribe(sub);
  }
  return client.connected();
}

void loop()
{
  Ethernet.maintain();
  if (!client.connected()) {
    long now = millis();
    if (now - lastReconnectAttempt > 5000) {
      lastReconnectAttempt = now;
      // Attempt to reconnect
      if (reconnect()) {
        Serial.println(now);
       Serial.println(lastReconnectAttempt);
        lastReconnectAttempt = 0;
      }
    }
  } else {
    // Client connected

    client.loop();
  }
}

void publishMessage(const char* topic, String payload , boolean retained)
{
  if (client.publish(topic, payload.c_str(), true))
  Serial.println("Message publised [" + String(topic) + "]: " + payload);
}
